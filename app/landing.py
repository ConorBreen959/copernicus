from flask import g, url_for, redirect
from flask_appbuilder import IndexView, expose


class MyIndexView(IndexView):
    @expose("/")
    def index(self):
        return redirect(url_for("HomeView.home"))


class MyBaseView(IndexView):
    index_template = "my_base.html"
