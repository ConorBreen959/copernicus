import os
from dotenv import load_dotenv, find_dotenv

from flask_appbuilder.const import AUTH_DB

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV")

    load_dotenv()

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = os.getenv("TESTING", "False").lower() == "true"
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY")

    DATE_FORMAT = "%d %b, %Y"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    ERROR_LOG = "error.log"

    # ------------------------------
    # GLOBALS FOR APP Builder
    # ------------------------------
    # Uncomment to set up Your App name
    APP_NAME = os.environ.get("APP_NAME", "Copernicus")
    APP_ICON = os.environ.get("APP_ICON", "/static/img/solar-logo.png")
    # APP_THEME = "flatly.css"

    # ----------------------------------------------------
    # AUTHENTICATION CONFIG
    # ----------------------------------------------------
    # The authentication type
    AUTH_TYPE = AUTH_DB

    # Will allow user self registration
    AUTH_USER_REGISTRATION = True

    # The default user self registration role
    AUTH_USER_REGISTRATION_ROLE = "BaseUser"

    SQLALCHEMY_POOL_RECYCLE = 7200
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Config for Flask-WTF Recaptcha necessary for user registration
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

    # API access token expiry
    JWT_ACCESS_TOKEN_EXPIRES = 10

    FAB_API_SWAGGER_UI = True

    # Flask-Mail Config
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_PORT = 587

    # Roles
    SUNRISE_ROLES = [
        ["Sunrise View", "menu_access"],
        ["SunriseView", "can_graph"],
        ["SunriseView", "can_this_form_get"],
        ["SunriseView", "can_this_form_post"],
        ["AstralPositions View", "menu_access"],
        ["AstralPositionsView", "can_comingsoon"],
    ]
    FAB_ROLES = {
        "Public": [
            ["MyIndex View", "menu_access"],
            ["Home View", "menu_access"],
            ["HomeView", "can_home"],
        ] + SUNRISE_ROLES,
        "BaseUser": [
            ["UserDBModelView", "can_userinfo"],
            ["UserDBModelView", "userinfoedit"],
            ["UserDBModelView", "resetmypassword"],
            ["UserDBModelView", "can_edit"],
            ["ResetMyPasswordView", "can_this_form_get"],
            ["ResetMyPasswordView", "can_this_form_post"],
            ["UserInfoEditView", "can_this_form_get"],
            ["UserInfoEditView", "can_this_form_post"],
            ["HomeView", "can_home"],
        ] + SUNRISE_ROLES,
        "SuperUser": [
            ["List Users", "menu_access"],
            ["Security", "menu_access"],
            ["UserDBModelView", "can_list"],
            ["UserDBModelView", "can_show"],
            ["UserDBModelView", "can_delete"],
            ["UserDBModelView", "resetpasswords"],
            ["ResetPasswordView", "can_this_form_get"],
            ["ResetPasswordView", "can_this_form_post"],
        ] + SUNRISE_ROLES,
    }

    # ---------------------------------------------------
    # Image and file configuration
    # ---------------------------------------------------

    # The file upload folder, when using models with files
    UPLOAD_FOLDER = BASEDIR + "/app/static/uploads/"
