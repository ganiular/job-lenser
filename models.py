from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base, db_session

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hashed = Column(String, nullable=False)
    account_type = Column(String, nullable=False)

class Applicant(Base):
    __tablename__ = 'applicants'
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    qualification_level = Column(Integer, ForeignKey("qualifications.level"), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    profile_picture = Column(String, nullable=False)
    resume = Column(String, nullable=False)
    skills = Column(String, nullable=False)
    qualification = relationship('Qualification', back_populates='applicant')
    user = relationship("User")

class Employer(Base):
    __tablename__ = 'employers'
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    # sector = Column(String, nullable=False)
    profile_picture = Column(String, nullable=False)
    user = relationship("User")
    job_offers = relationship("JobOffer", back_populates="employer")

class Qualification(Base):
    __tablename__ = 'qualifications'
    name = Column(String, nullable=False, unique=True)
    level = Column(Integer, nullable=False, unique=True, primary_key=True)
    applicant = relationship('Applicant', back_populates='qualification')

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer,primary_key=True, autoincrement="auto")
    name = Column(String, nullable=False, unique=True)

class JobOffer(Base):
    __tablename__ = 'job_offers'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    employer_id = Column(Integer, ForeignKey('employers.user_id'))
    title = Column(String, nullable=False)
    # location = Column(String, nullable=False)
    description = Column(String, nullable=False)
    min_qualification_level = Column(Integer, ForeignKey("qualifications.level"), nullable=False)
    min_qualification = relationship('Qualification')
    skills = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    employer = relationship("Employer", back_populates='job_offers')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    sender_id = Column(Integer, ForeignKey('employers.user_id'))
    receiver_id = Column(Integer, ForeignKey('applicants.user_id'))
    message = Column(String, nullable=False)
    job_offer_id = Column(Integer, ForeignKey('job_offers.id'))
    sender = relationship("Employer")
    receiver = relationship("Applicant")
    job_offer = relationship('JobOffer')
    time_created = Column(DateTime(timezone=True), server_default=func.current_timestamp())

def pulate_users():
    from datetime import date
    user1 = User(name='Bob Alice', email='user1@example.com', phone='08030424356', password_hashed='pbkdf2:sha256:260000$NLH6aGzmd1mIX07e$3f481d32ce597f3fa3c5c30984f065f3bf84069936874e773d72937cbf48574b', account_type='applicant')
    user2 = User(name='Mr Joel Smith', email='user2@example.com', phone='08079427821', password_hashed='pbkdf2:sha256:260000$NLH6aGzmd1mIX07e$3f481d32ce597f3fa3c5c30984f065f3bf84069936874e773d72937cbf48574b', account_type='employer')
    db_session.add(user1)
    db_session.add(user2)
    db_session.flush()

    applicant = Applicant(
        user_id=user1.id,
        qualification_level = 4,
        date_of_birth = date.fromisoformat('2017-03-21'),
        profile_picture='',
        resume='',
        skills='coding,eat,play'
    )

    employer = Employer(
        user_id=user2.id, 
        # sector='Faculty of Computing', 
        profile_picture=''
    )

    db_session.add(applicant)
    db_session.add(employer)
    db_session.commit()

def pulate_qualifications():
    qualifications = [
        ("Doctorate",	1),
        ("Master's Degree",	2),
        ("Postgraduate Diploma",	3),
        ("Bachelor's Degree",	4),
        ("Higher National Diploma",	5),
        ("National Diploma",	6),
        ("Undergraduate",	7),
        ("Secondary Schl Cert.",	8),
        ("Primary Schl Cert.",	9)
    ]
    for q, l in qualifications:
        db_session.add(
            Qualification(name=q, level=l)
        )
    db_session.commit()

def pulate_skills():
    skills = ['communication', 'driving', 'hardwording']
    for sk in skills:
        db_session.add(Skill(name=sk))
    db_session.commit()