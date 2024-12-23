from datetime import date

from flask_appbuilder.forms import DynamicForm
from wtforms import SelectField
from wtforms.fields.datetime import DateField

from app.models import CityLocations


class SunriseForm(DynamicForm):
    city_locations = CityLocations.query.all()
    locations = [("", "")]
    for city in city_locations:
        locations.append((city.city_name, city.city_name))
    location = SelectField("Select Location", choices=locations, default="Dublin, Ireland")
    date_select = DateField("Select Date", default=date.today())


class CopernicusForm(DynamicForm):
    start_date = DateField("Start Date", default=date.today())
    end_date = DateField("End Date", default=date.today())
    objects = [
        ("", ""),
        ("Sun", "Sun"),
        ("Mercury", "mercury"),
        ("Venus", "venus"),
        ("Mars", "mars"),
        ("Jupiter", "jupiter"),
        ("Saturn", "saturn"),
    ]
    body = SelectField("Select Planetary Body", choices=objects)

