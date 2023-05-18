import os
from datetime import date
from flask import Blueprint, render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from database import db_session as db
from models import Skill, User, Applicant, Employer, Qualification


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

    session.clear()
    session['account_type'] = user.account_type
    session['user_id'] = user.id
    return redirect('/')

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
    # if user.account_type == 'applicant':
    #     applicant = db.query(Applicant).filter(Applicant.user_id == user.id).first()

    #     if applicant is None:
    #         session['temporary_id'] = user.id
    #         return redirect('/signup_applicant')
    # else:
    #     employer = db.query(Employer).filter(Employer.user_id == user.id).first()
    #     if employer is None:
    #         session['temporary_id'] = user.id
    #         return redirect('/signup_employer')
    session['user_id'] = user.id
    return redirect('/')

@bp.get('/signout')
def signout():
    # Clear user session from the client
    session.clear()
    return redirect('/')            


@bp.get('/signup_employer')
def signup_employer():
    return render_template('signup_employer.html')

@bp.post('/signup_employer')
def signup_employer_post():
    # get all form fields
    name = request.form.get('name', '').strip()
    account_type = 'employer'
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    # sector = request.form.get('org-name')
    org_picture = request.files.get('org-picture')

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
        return render_template('signup_employer.html', error=error)
    
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
    
    employer = Employer(user_id=user.id, profile_picture=org_picture.filename)
    db.add(employer)
    
    picture_path = os.path.join('uploads','profile-pictures',str(user.id))
    
    if not os.path.exists(picture_path):
        os.makedirs(picture_path)
    
    org_picture.save(os.path.join(picture_path, org_picture.filename))
    
    db.commit()
    
    session.clear()
    session['account_type'] = user.account_type
    session['user_id'] = user.id
    return redirect('/')
    

@bp.get('/signup_applicant')
def signup_applicant():
    qualifications = db.query(Qualification).order_by(Qualification.level.desc()).all()
    skills = db.query(Skill).all()
    error = None
    for msg in get_flashed_messages():
        error = msg
    
    return render_template('signup_applicant.html', qualifications=qualifications, skills=skills, error=error);

@bp.post('/signup_applicant')
def signup_applicant_post():
    # get all form fields
    name = request.form.get('name', '').strip()
    account_type = 'applicant'
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    dob = request.form.get('date-of-birth')
    qualification = request.form.get('qualification')
    p_picture = request.files.get('p-picture')
    resume = request.files.get('resume')
    
    skills = []
    for skill in request.form.getlist('skills'):
        if skill:
            skills.append(skill)
    skills = ','.join(skills)

    print(request.form)
    
    # validate inputs
    error = None
    if not(name and email and phone and password and cpassword):
        error='All fields are required'
    elif not(name.isalpha()) and len(name) < 3:
        error = "Invalid name"
    elif account_type not in ['applicant', 'employer']:
        error='Invalid account type'
    elif not phone.isdigit():
        error='Invalid phone number'
    elif not skills:
        error='Select one or more skills'
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
        flash(error)
        return redirect('/signup_applicant')

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

    applicant = Applicant(
        user_id=user.id,
        qualification_level = qualification,
        date_of_birth = date.fromisoformat(dob),
        profile_picture=p_picture.filename,
        resume=resume.filename,
        skills=skills
    )
    db.add(applicant)
    
    # save uploaded files
    # create directories if not exist
    picture_path = os.path.join('uploads','profile-pictures',str(user.id))
    resume_path = os.path.join('uploads', 'resumes', str(user.id))
    
    if not os.path.exists(picture_path):
        os.makedirs(picture_path)
    if not os.path.exists(resume_path):
        os.makedirs(resume_path)
    
    p_picture.save(os.path.join(picture_path, p_picture.filename))
    resume.save(os.path.join(resume_path, resume.filename))

    db.commit()
    session.clear()
    session['account_type'] = user.account_type
    session['user_id'] = user.id
    return redirect('/')
