from flask import Blueprint, render_template, request, redirect, session
import db

bp = Blueprint('auth', __name__)

@bp.get('/signup')
def signup():
    return render_template('signup.html')

@bp.post('/signup')
def signup_post():
    # get all form fields
    account_type = request.form.get('account-type')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    conn = db.connect()

    # validate inputs
    error = None
    if not(account_type and email and phone and password and cpassword):
        error='All fields are required'
    elif account_type not in ['applicant', 'employer']:
        error='Invalid account type'
    elif not phone.isdigit():
        error='Invalid phone number'
    elif len(password) < 6:
        error='Password too shot'
    elif password != cpassword:
        error='Password mismatch'
    else:
        user = conn.execute('SELECT * FROM users WHERE email=?', [email]).fetchone()
        if user is not None:
            error='The email is ready registered'

    if error is not None:
        return render_template('signup.html', error=error)
    
    # now that the input fields as been validated, keep user credentials
    conn.execute(
        'INSERT INTO users(email, phone, password, account_type) VALUES(?,?,?,?)',
        [email, phone, password, account_type])
    conn.commit()

    return redirect('/signin')

@bp.get('/signin')
def signin():
    return render_template('signin.html')

@bp.post('/signin')
def signin_post():
    # get all form fields
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = db.connect()

    # validate inputs
    error = None
    if not(email and password):
        error='All fields are required'
    else:
        user = conn.execute('SELECT * FROM users WHERE email=?', [email]).fetchone()
        if user is None:
            error='Unkown user'
        elif user['password'] != password:
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
    session['account_type'] = user['account_type']
    if user['account_type'] == 'applicant':
        applicant = conn.execute(
            'SELECT * FROM applicants WHERE user_id=?', [user['id']]
        ).fetchone()
        if applicant is None:
            session['temporary_id'] = user['id']
            return redirect('/signup_applicant')
    else:
        employer = conn.execute(
            'SELECT * FROM employer WHERE user_id=?', [user['id']]
        ).fetchone()
        if employer is None:
            session['temporary_id'] = user['id']
            return redirect('/signup_employer')
    session['user_id'] = user['id']
    return redirect('/')
            

# NOTE: These pages can only be visited, after user have logged in

@bp.get('/signup_employer')
def signup_employer():
    return render_template('signup_employer.html')

@bp.get('/signup_applicant')
def signup_applicant():
    return render_template('signup_applicant.html')

