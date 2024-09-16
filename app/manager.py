import os

from flask_appbuilder.security.sqla.models import User, Role

from app.models import db


def seed_users():
    from . import appbuilder

    base = Role.query.filter_by(name="BaseUser").first()
    if not User.query.filter_by(username="admin").first():
        admin = Role.query.filter_by(name="Admin").first()
        appbuilder.sm.add_user(
            "admin",
            "Conor",
            "Breen",
            "conor.breen+admin@plusvital.com",
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
            "conor.breen+teststaff@plusvital.com",
            [base, staff],
            os.environ.get("USER_PASS"),
        )
        db.session.commit()
