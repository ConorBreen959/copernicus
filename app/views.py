import json
from flask import g, render_template, jsonify, request
from flask_appbuilder import BaseView, SimpleFormView, expose
from flask_appbuilder.widgets import ListWidget

from app import appbuilder
from app.forms import SunriseForm
from app.utils.sunrise import SunriseGraph


class SunriseWidget(ListWidget):
    template = "widgets/sunrise.html"


class SunriseView(SimpleFormView):
    route_base = "/sunriseview"
    form = SunriseForm
    form_title = "Sunrise"
    edit_widget = SunriseWidget

    sun_graph = SunriseGraph()
    location = "Dublin, Ireland"
    sun_graph.set_timezone(location)
    sun_graph.set_year(2024)
    sunrise_data = sun_graph.format_sunrise_data()
    sunrise_graph = sun_graph.create_graph(sunrise_data)

    @expose("/graph/", methods=["GET", "POST"])
    def graph(self):
        if self.form.validate_on_submit:
            location = request.args.get("location")
            if location != self.location:
                self.sun_graph.set_timezone(location)
                self.sun_graph.set_year(2024)
                sunrise_data = self.sun_graph.format_sunrise_data()
                self.sunrise_graph = self.sun_graph.create_graph(sunrise_data)
            return jsonify(json.loads(self.sunrise_graph))


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
        return self.render_template("logged_user.html", greeting=greeting)


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
