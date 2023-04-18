from flask import Blueprint, render_template, session, redirect, request, abort
from database import db_session as db
from models import Applicant, Employer, JobOffer, Message, User

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
    user_id = session.get('user_id')
    if user_id is None:
        return render_template('index.html')
    else:
        return redirect('/profile/'+ str(user_id))

# View any user profile page
@bp.get('/profile/<int:user_id>')
def profile(user_id):
    # know the account type of the user
    
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
    conn = db.connect()

    if(account_type == 'applicant'):
        applicant = conn.execute(
            
        )

@bp.get('/profile/messages')
def message_list():
    user_id = session['user_id']
    if session['account_type'] == 'applicant':
        applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
        messages = db.query(Message).filter(Message.receiver_id == user_id).all()
        return render_template('inbox_message_list.html', messages=messages, applicant=applicant)
    else:
        employer = db.query(Employer).filter(Employer.user_id == user_id).first()
        messages = db.query(Message).filter(Message.sender_id == user_id).all()
        return render_template('outbox_message_list.html', messages=messages, employer=employer)


@bp.get('/profile/messages/<int:applicant_id>')
def message(applicant_id):
    # only employer can send message
    if session['account_type'] != 'employer':
        abort(403)
    
    employer_id = session['user_id']
    employer = db.query(Employer).filter(Employer.user_id == employer_id).first()
    applicant = db.query(Applicant).filter(Applicant.user_id == applicant_id).first()

    return render_template('message.html', employer=employer, applicant=applicant)

@bp.post('/profile/messages/<int:applicant_id>')
def message_post(applicant_id):
    job_offer_id = request.form['job_offer']
    message = request.form['message'].strip()
    employer_id = session['user_id']

    message = Message(
        sender_id = employer_id,
        receiver_id = applicant_id,
        message = message,
        job_offer_id = job_offer_id
    )
    db.add(message)
    db.commit()
    return redirect(f'/profile/messages')
    