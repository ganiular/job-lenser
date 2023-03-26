from flask import Blueprint, render_template, session, redirect, request, abort
import db

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
    conn = db.connect()
    user = conn.execute(
        'SELECT * FROM users WHERE id=?', [user_id]
    ).fetchone()
    if user is None:
        # stop the resquest with page not found
        abort(404)
    else:
        if user['account_type'] == 'applicant':
            applicant = conn.execute(
                'SELECT * FROM users JOIN applicants ON users.id=applicants.user_id '
                'JOIN qualifications ON applicants.qualification_id=qualifications.id WHERE users.id=?',
                [user_id]).fetchone()
            return render_template('profile.html', applicant=applicant, user_id=user_id)
        else:
            employer = conn.execute(
                'SELECT * FROM users JOIN employers ON users.id=employers.user_id WHERE users.id=?',
                [user_id]).fetchone()
            return render_template('profile.html', employer=employer, user_id=user_id)
        
@bp.get('/profile/edit')
def edit_profile():
    user_id = session['user_id']
    account_type = session['account_type']
    conn = db.connect()

    if(account_type == 'applicant'):
        applicant = conn.execute(
            
        )