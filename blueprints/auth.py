import os
from datetime import date
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import db_session as db
from models import User, Applicant, Employer, Qualification


bp = Blueprint('auth', __name__)

@bp.get('/signup')
def signup():
    return render_template('signup.html')

@bp.post('/signup')
def signup_post():
    # get all form fields
    name = request.form.get('name', '').strip()
    account_type = request.form.get('account-type')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    # conn = db.connect()

    # validate inputs
    error = None
    if not(name and account_type and email and phone and password and cpassword):
        error='All fields are required'
    elif not(name.isalpha()) and len(name) < 3:
        error = "Invalid name"
    elif account_type not in ['applicant', 'employer']:
        error='Invalid account type'
    elif not phone.isdigit():
        error='Invalid phone number'
    elif len(password) < 6:
        error='Password too shot'
    elif password != cpassword:
        error='Password mismatch'
    else:
        user = db.query(User).filter(User.email == email).first()
        print(user)
        # user = conn.execute('SELECT * FROM users WHERE email=?', [email]).fetchone()
        if user is not None:
            error='The email is ready registered'

    if error is not None:
        return render_template('signup.html', error=error)
    
    # keep password secret by tranforming it
    password_hashed = generate_password_hash(password)

    # now that the input fields as been validated, keep user credentials
    user = User(
        name=name, 
        email=email, 
        phone=phone, 
        password_hashed=password_hashed, 
        account_type=account_type
    )
    db.add(user)
    db.commit()
    
    return redirect('/signin')

@bp.get('/signin')
def signin():
    return render_template('signin.html')

@bp.post('/signin')
def signin_post():
    # get all form fields
    email = request.form.get('email')
    password = request.form.get('password')

    # validate inputs
    error = None
    if not(email and password):
        error='All fields are required'
    else:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            error='Unkown user'
        elif not check_password_hash(user.password_hashed, password):
            error='Incorrect password'

    if error is not None:
        return render_template('signin.html', error=error)
    
    # Now that the input fields has been validated,
    # but the user may or may not have finished his registeration.
    # I will check to see if user had registered finish,
    # if yes, I will store a key named temporary_id in the client session
    # and redirect user to complete his registration
    # otherwise i will name the key user_id and direct user
    # to index page.
    # Clear any prevoius user session, and create a new one
    session.clear()
    session['account_type'] = user.account_type
    if user.account_type == 'applicant':
        applicant = db.query(Applicant).filter(Applicant.user_id == user.id).first()

        if applicant is None:
            session['temporary_id'] = user.id
            return redirect('/signup_applicant')
    else:
        employer = db.query(Employer).filter(Employer.user_id == user.id).first()
        if employer is None:
            session['temporary_id'] = user.id
            return redirect('/signup_employer')
    session['user_id'] = user.id
    return redirect('/')

@bp.get('/signout')
def signout():
    # Clear user session from the client
    session.clear()
    return redirect('/')            

# NOTE: These pages can only be visited, after user have logged in

@bp.get('/signup_employer')
def signup_employer():
    # requires temporary_id or user_id in the client session
    # and account_type == applicant
    temporary_id = session.get('temporary_id')
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    if not(temporary_id or user_id):
        return redirect('/signin')
    elif account_type != 'employer':
        return redirect('/signup_applicant')
    
    return render_template('signup_employer.html')

@bp.post('/signup_employer')
def signup_employer_post():
    sector = request.form.get('org-name')
    org_picture = request.files.get('org-picture')
    
    user_id = session.get('user_id') or session.get('temporary_id')
    
    employer = Employer(user_id=user_id, sector=sector, profile_picture=org_picture.filename)
    db.add(employer)
    
    picture_path = os.path.join('uploads','profile-pictures',str(user_id))
    
    if not os.path.exists(picture_path):
        os.makedirs(picture_path)
    
    org_picture.save(os.path.join(picture_path, org_picture.filename))
    
    # remove temporary_id and set user_id
    session.pop('temporary_id')
    session['user_id'] = user_id

    db.commit()
    
    return redirect('/')
    

@bp.get('/signup_applicant')
def signup_applicant():
    # requires temporary_id or user_id in the client session
    # and account_type == applicant
    temporary_id = session.get('temporary_id')
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    if not(temporary_id or user_id):
        return redirect('/signin')
    elif account_type != 'applicant':
        return redirect('/signup_employer')
    
    qualifications = db.query(Qualification).order_by(Qualification.level.desc()).all()
    
    return render_template('signup_applicant.html', qualifications=qualifications)

@bp.post('/signup_applicant')
def signup_applicant_post():
    dob = request.form.get('date-of-birth')
    print(dob)
    qualification = request.form.get('qualification')
    p_picture = request.files.get('p-picture')
    resume = request.files.get('resume')
    
    # remove spaces and convert it to lowercase
    skills = request.form.get('skills').replace(' ', '').strip(',').lower()
    
    user_id = session.get('user_id') or session.get('temporary_id')

    applicant = Applicant(
        user_id=user_id,
        qualification_level = qualification,
        date_of_birth = date.fromisoformat(dob),
        profile_picture=p_picture.filename,
        resume=resume.filename,
        skills=skills
    )
    db.add(applicant)
    
    # save uploaded files
    # create directories if not exist
    picture_path = os.path.join('uploads','profile-pictures',str(user_id))
    resume_path = os.path.join('uploads', 'resumes', str(user_id))
    
    if not os.path.exists(picture_path):
        os.makedirs(picture_path)
    if not os.path.exists(resume_path):
        os.makedirs(resume_path)
    
    p_picture.save(os.path.join(picture_path, p_picture.filename))
    resume.save(os.path.join(resume_path, resume.filename))

    # remove temporary_id and set user_id
    session.pop('temporary_id')
    session['user_id'] = user_id

    db.commit()
    
    return redirect('/')
