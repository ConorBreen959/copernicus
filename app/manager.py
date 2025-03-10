import os
import pandas as pd
from flask_appbuilder.security.sqla.models import User, Role

from app.models import db, CityLocations


def seed_users():
    from . import appbuilder

    base = Role.query.filter_by(name="BaseUser").first()
    if not User.query.filter_by(username="admin").first():
        admin = Role.query.filter_by(name="Admin").first()
        appbuilder.sm.add_user(
            "admin",
            "Conor",
            "Breen",
            "conor.breen32+admin@gmail.com",
            [admin],
            os.environ.get("SUPERUSER_PASS"),
        )
        db.session.commit()
    if (
        not User.query.filter_by(username="teststaff").first()
        and appbuilder.app.config["FLASK_ENV"] != "prod"
    ):
        staff = Role.query.filter_by(name="Staff").first()
        appbuilder.sm.add_user(
            "testuser",
            "Test",
            "User",
            "conor.breen32+test@gmail.com",
            [base, staff],
            os.environ.get("USER_PASS"),
        )
        db.session.commit()


def seed_data():
    check_table_data = CityLocations.query.first()
    if not check_table_data:
        data = pd.read_csv("app/static/city_locations.tsv", sep="\t")
        add_city_locations(data)


def add_city_locations(data):
    user = User.query.filter_by(username="admin").first()
    for row in data.itertuples():
        city_in_db = CityLocations.query.filter_by(city_name=row.city_name).first()
        if not city_in_db:
            city = CityLocations(
                city_name=row.city_name,
                latitude=row.latitude,
                longitude=row.longitude,
                created_by=user,
                changed_by=user
            )
            db.session.add(city)
    db.session.commit()
