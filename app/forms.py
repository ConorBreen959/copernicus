from datetime import date

from flask_appbuilder.forms import DynamicForm
from wtforms import SelectField


class SunriseForm(DynamicForm):
    locations = [
        ("", ""),
        ("Dublin, IE", "Dublin, IE"),
        ("Nairobi", "Nairobi")
    ]
    location = SelectField("Select Location", choices=locations)

#
# class CopernicusForm(DynamicForm):
#     start_date = DateField("Start Date", default=date.today())
#     end_date = DateField("End Date", default=date.today())
#     objects = [
#         ("", ""),
#         ("Sun", "Sun"),
#         ("Mercury", "mercury"),
#         ("Venus", "venus"),
#         ("Mars", "mars"),
#         ("Jupiter", "jupiter"),
#         ("Saturn", "saturn"),
#     ]
#     body = SelectField("Select Planetary Body", choices=objects)
