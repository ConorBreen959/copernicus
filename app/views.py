import json
from datetime import date
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
    form_title = "Sunrise"
    edit_widget = SunriseWidget

    sun_graph = SunriseGraph()
    date = date.today().strftime("%Y-%m-%d")
    location = "Dublin, Ireland"
    city_location = CityLocations.query.filter_by(city_name=location).first()
    city_dict = city_location.to_json()
    sun_graph.set_timezone(city_dict)
    sun_graph.set_year(2024)
    sunrise_data = sun_graph.format_sunrise_data()
    sunrise_chart = sun_graph.create_graph(sunrise_data)
    date_line = sun_graph.add_date_line(date)
    chart_with_line = sunrise_chart + date_line
    date_chart = sun_graph.create_date_chart(date, sunrise_data)
    json_packet = {
        "sunrise_chart": json.loads(chart_with_line.to_json()),
        "date_chart": json.loads(date_chart.to_json())
    }

    @expose("/graph/", methods=["GET", "POST"])
    def graph(self):
        if self.form.validate_on_submit:
            location = request.args.get("location")
            date = request.args.get("date_select")
            if location != self.location:
                city_location = CityLocations.query.filter_by(city_name=location).first()
                city_dict = city_location.to_json()
                self.sun_graph.set_timezone(city_dict)
                self.sun_graph.set_year(2024)
                self.sunrise_data = self.sun_graph.format_sunrise_data()
                self.sunrise_chart = self.sun_graph.create_graph(self.sunrise_data)
            if date != self.date:
                self.date_line = self.sun_graph.add_date_line(date)
                self.date_chart = self.sun_graph.create_date_chart(date, self.sunrise_data)
                self.json_packet["date_chart"] = json.loads(self.date_chart.to_json())
            self.chart_with_line = self.sunrise_chart + self.date_line
            self.json_packet["sunrise_chart"] = json.loads(self.chart_with_line.to_json())
            return jsonify(self.json_packet)
        return jsonify(self.json_packet)


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
