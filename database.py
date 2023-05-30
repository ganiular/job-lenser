from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


engine = create_engine('sqlite:///./appdata2.db')
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(session)

Base = declarative_base()
# Base.query = db_session.query_property()

def init_db():
    from models import pulate_qualifications, pulate_users, pulate_skills
    import shutil

    Base.metadata.create_all(bind=engine)

    # try write initial values into database
    # and remove uploaded files
    try:
        pulate_qualifications()
        # pulate_users()
        pulate_skills()
        shutil.rmtree('uploads')
    except:
        db_session.rollback()
        print('Already pulated')
    
# Regsiter this function with the app response closure listener
# to help close the database connection regardless of error
def on_response_close(exception=None):
    if exception is not None:
        print('Error on_response_close:', exception)
    db_session.remove()
