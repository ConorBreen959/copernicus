import json
import logging
from datetime import datetime
from flask import render_template, jsonify, request
from flask_appbuilder import BaseView, SimpleFormView, expose
from flask_appbuilder.widgets import ListWidget

from app import appbuilder
from app.forms import SunriseForm
from app.models import CityLocations
from app.utils.sunrise import SunriseGraph


class SunriseWidget(ListWidget):
    template = "widgets/sunrise.html"


class SunriseView(SimpleFormView):
    route_base = "/sunriseview"
    form = SunriseForm
    form_title = "Sunrise Graph"
    edit_widget = SunriseWidget

    defaults = {
        "location": "Dublin, Ireland",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    city_location = CityLocations.query.filter_by(city_name=defaults["location"]).first()
    city_dict = city_location.to_json()
    sun_graph = SunriseGraph(city_dict, defaults["date"])

    @expose("/graph/", methods=["GET", "POST"])
    def graph(self):
        if self.form.validate_on_submit:
            location = request.args.get("location")
            date = request.args.get("date_select")
            if location != self.defaults["location"]:
                city_location = CityLocations.query.filter_by(city_name=location).first()
                city_dict = city_location.to_json()
                self.sun_graph = SunriseGraph(city_dict, date)
            sunrise_chart, date_chart = self.sun_graph.create_charts(date)
            json_packet = {
                "sunrise_chart": json.loads(sunrise_chart.to_json()),
                "date_chart": json.loads(date_chart.to_json())
            }
            return jsonify(json_packet)


class AstralPositionsView(BaseView):
    route_base = "/astralpositionsview"
    default_view = "comingsoon"

    @expose("/comingsoon/", methods=["GET"])
    def comingsoon(self):
        return self.render_template("widgets/astral_positions.html")


class HomeView(BaseView):
    route_base = "/"

    @expose("/home/")
    def home(self):
        # user = g.user
        #
        # if user.is_anonymous:
        #     user = User.query.filter_by(username="publicuser").first()
        #     login_user(user)

        greeting = "Greetings!"
        return self.render_template("index.html", greeting=greeting)


class HealthView(BaseView):
    route_base = "/health"

    @expose("/check/")
    def check(self):
        greeting = "Hello World"
        return self.render_template("logged_user.html", greeting=greeting)


@appbuilder.app.after_request
def add_header(response):
    response.cache_control.private = True
    response.cache_control.public = False
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
