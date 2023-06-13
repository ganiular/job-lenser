from datetime import date
import os
from flask import Blueprint, flash, get_flashed_messages, render_template, session, redirect, request, abort
from sqlalchemy import desc
from werkzeug.security import generate_password_hash
from database import db_session as db
from models import Applicant, Employer, JobOffer, Message, Qualification, Skill, User

bp = Blueprint('account', __name__)


# if client session is having temporary_id, which means he has not
# finish his account registration. Redirect him to appropate page to 
# complete his registration before he can visit any page here
@bp.before_request
def must_complete_account_registration():
    temporary_id = session.get('temporary_id')
    if temporary_id is not None:
        if session['account_type'] == 'applicant':
            return redirect('/signup_applicant')
        else:
            return redirect('/signup_employer')

@bp.before_request
def must_login():
    # except for index page
    if request.path == '/':
        return
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/')
    
@bp.get('/')
def index():
    return render_template('index.html')

# View any user profile page
@bp.get('/profile/<int:user_id>')
def profile(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # stop the resquest with page not found
        abort(404)
    else:
        if user.account_type == 'applicant':
            applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
            return render_template('profile_applicant.html', applicant=applicant, user_id=user_id)
        else:
            employer = db.query(Employer).filter(Employer.user_id == user_id).first()
            return render_template('profile_employer.html', employer=employer, user_id=user_id)
        
@bp.get('/profile/edit')
def edit_profile():
    user_id = session['user_id']
    account_type = session['account_type']
    
    if(account_type == 'applicant'):
        applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
        qualifications = db.query(Qualification).order_by(Qualification.level.desc()).all()
        skills = db.query(Skill).all()
        error = None
        for msg in get_flashed_messages():
            error = msg
        
        return render_template('signup_applicant.html', qualifications=qualifications, skills=skills, error=error, applicant=applicant)
    else:
        employer = db.query(Employer).filter(Employer.user_id == user_id).first()
        return render_template('signup_employer.html', employer=employer)

@bp.post('/profile/edit')
def update_profile():
    # get all form fields
    name = request.form.get('name', '').strip()
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    dob = request.form.get('date-of-birth')
    qualification = request.form.get('qualification')
    p_picture = request.files.get('p-picture')
    org_picture = request.files.get('org-picture')
    resume = request.files.get('resume')
    skills = []
    for skill in request.form.getlist('skills'):
        if skill:
            skills.append(skill)
    skills = ','.join(skills)

    user_id = session['user_id']
    account_type = session['account_type']
    error = None
    
    if password != '':
        if len(password) < 6:
            error = 'Password too short'
        elif password != cpassword:
            error='Password mismatch'
    
    if error:
        flash(error)
        return redirect('/profile/edit')
    
    values = {}
    values[User.name] = name
    values[User.email] = email
    values[User.phone] = phone
    if password:
        values[User.password_hashed] = generate_password_hash(password)
    
    db.query(User).filter(User.id == user_id).update(values, synchronize_session=False)
    
    if(account_type == 'applicant'):
        values = {}
        values[Applicant.qualification_level] = qualification
        values[Applicant.date_of_birth] = date.fromisoformat(dob)
        values[Applicant.skills] = skills
        if p_picture:
            values[Applicant.profile_picture] = p_picture.filename
            picture_path = os.path.join('uploads','profile-pictures',str(user_id))
            p_picture.save(os.path.join(picture_path, p_picture.filename))
        if resume:
            values[Applicant.resume] = resume.filename
            resume_path = os.path.join('uploads', 'resumes', str(user_id))
            resume.save(os.path.join(resume_path, resume.filename))
        db.query(Applicant).filter(Applicant.user_id == user_id) \
        .update(values, synchronize_session=False)
    else:
        if org_picture:
            count = db.query(Employer).filter(Employer.user_id == user_id) \
                .update({Employer.profile_picture: org_picture.filename})
            if count > 0:
                picture_path = os.path.join('uploads','profile-pictures',str(user_id))
                org_picture.save(os.path.join(picture_path, org_picture.filename))

    db.commit()
    return redirect('/profile/%d' %user_id)
    
@bp.get('/chats')
def chat_list():
    user_id = session['user_id']
    if session['account_type'] == 'applicant':
        me = db.query(Applicant).filter(Applicant.user_id == user_id).first()
        messages = db.query(Message).group_by(Message.employer_id).filter(Message.applicant_id == user_id).all()
        return render_template('chat_list.html', messages = messages, me=me)
    else:
        me = db.query(Employer).filter(Employer.user_id == user_id).first()
        messages = db.query(Message).group_by(Message.applicant_id).filter(Message.employer_id == user_id).all()
        return render_template('chat_list.html', messages = messages, me=me)

@bp.get('/chats/<partner_id>')
def message_list(partner_id):
    user_id = session['user_id']
    if session['account_type'] == 'applicant':
        partner = db.query(Employer).filter(Employer.user_id == partner_id).first()
        messages = db.query(Message).filter(Message.employer_id == partner_id, Message.applicant_id == user_id).all()
        return render_template('message_list.html', messages = messages, partner=partner)
    else:
        partner = db.query(Applicant).filter(Applicant.user_id == partner_id).first()
        messages = db.query(Message).filter(Message.employer_id == user_id, Message.applicant_id == partner_id).all()
        return render_template('message_list.html', messages = messages, partner=partner)

@bp.get('/profile/messages')
def _message_list():
    user_id = session['user_id']
    if session['account_type'] == 'applicant':
        applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
        messages = db.query(Message).filter(Message.receiver_id == user_id).all()
        return render_template('inbox_message_list.html', messages=messages, applicant=applicant)
    else:
        employer = db.query(Employer).filter(Employer.user_id == user_id).first()
        messages = db.query(Message).filter(Message.sender_id == user_id).all()
        return render_template('outbox_message_list.html', messages=messages, employer=employer)


@bp.get('/profile/messages/<int:receiver_id>')
def message(receiver_id):
    # # only employer can send message
    # if session['account_type'] != 'employer':
    #     abort(403)
    
    sender_id = session['user_id']
    if session['account_type'] == 'employer':
        employer = db.query(Employer).filter(Employer.user_id == sender_id).first()
        applicant = db.query(Applicant).filter(Applicant.user_id == receiver_id).first()
    else:
        employer = db.query(Employer).filter(Employer.user_id == receiver_id).first()
        applicant = db.query(Applicant).filter(Applicant.user_id == sender_id).first()
    
    return render_template('message.html', employer=employer, applicant=applicant)

@bp.post('/profile/messages/<int:receiver_id>')
def message_post(receiver_id):
    job_offer_id = request.form.get('job_offer')
    message = request.form['message'].strip()
    sender_id = session['user_id']

    if session['account_type'] == 'employer':
        employer_id = sender_id
        applicant_id = receiver_id
    else:
        employer_id = receiver_id
        applicant_id = sender_id

    message = Message(
        sender_id = sender_id,
        employer_id = employer_id,
        applicant_id = applicant_id,
        message = message,
        job_offer_id = job_offer_id
    )
    db.add(message)
    db.commit()
    return redirect(f'/chats/{receiver_id}')
    