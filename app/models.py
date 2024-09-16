from flask_appbuilder import SQLA, Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base

db = SQLA(session_options={"autoflush": False})
Base = declarative_base()


class CityLocations(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    city_name = Column(String(512))
    latitude = Column(DECIMAL(8, 7))
    longitude = Column(DECIMAL(8, 7))