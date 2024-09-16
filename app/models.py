from flask_appbuilder import SQLA
from sqlalchemy.orm import declarative_base

db = SQLA(session_options={"autoflush": False})
Base = declarative_base()
