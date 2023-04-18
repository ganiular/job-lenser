from flask import Blueprint, request, session, redirect, render_template, abort
from database import db_session as db
from models import Applicant, Employer, JobOffer, Qualification

bp = Blueprint('job', __name__)

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
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/')
    
@bp.get('/jobs')
def create_job():
    qualifications = db.query(Qualification).order_by(Qualification.level.desc()).all()

    return render_template('create_job.html', qualifications=qualifications)

@bp.post('/jobs')
def create_job_post():
    # validate user
    # required that only employer can send this request
    user_id = session.get('user_id')
    employer = db.query(Employer).filter(Employer.user_id == user_id).first()
    if not employer:
        return redirect('/')
    
    title = request.form['title'].strip()
    description = request.form['description'].strip()
    location = request.form['location'].strip()
    min_qualification = request.form['qualification']

    # remove spaces and convert it to lowercase
    skills = request.form.get('skills').replace(' ', '').strip(',').lower()
    

    # validate inputs
    error = None
    if not(title and description and location):
        error = 'All fields are required'

    if error is not None:
        return render_template('create_job.html', error=error)
    
    job_offer = JobOffer(
        employer_id=user_id, 
        title=title, 
        description=description, 
        location=location,
        min_qualification_level=min_qualification,
        skills=skills
    )
    db.add(job_offer)
    db.commit()

    return redirect(f'/jobs/{job_offer.id}')

@bp.get('/jobs/<int:job_id>')
def job(job_id):
    job_offer = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    if job_offer is None:
        # stop the resquest with page not found
        abort(404)


    job_offer_skills = job_offer.skills.split(',')
    applicants = db.query(Applicant).filter(
        Applicant.qualification_level <= job_offer.min_qualification_level).all()
    for applicant in applicants:
        count = 0
        for skill in applicant.skills.split(','):
            if skill in job_offer_skills:
                count += 1
        applicant.accuracy = int(70 * count / len(job_offer_skills))
        applicant.accuracy += int(30 / (job_offer.min_qualification_level - applicant.qualification_level))
    
    sorted(applicants, key=lambda x: x.accuracy, reverse=True)
    return render_template('job.html', job_offer=job_offer, applicants=applicants)

