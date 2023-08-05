import logging
import json
from functools import lru_cache
import flask
from flask import session

from flask_login import LoginManager, login_user, login_required, logout_user
from flask_login.mixins import UserMixin

from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

logger = logging.getLogger()


class DummyUser(UserMixin):
    """
    A Dummy User class
    """

    def __init__(self, id, email):
        self.id = id
        self.email = email

    def __repr__(self):
        return "<%s %r %r>" % (self.__class__.__name__, self.id, self.email)


def load_user(user_id):
    return DummyUser(user_id, "test@example.com")


class LoginForm(FlaskForm):
    """
    A simple login form
    """

    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


def get_user():
    user_id = session.get("user_id")
    if user_id:
        return load_user(user_id)
    else:
        return {}


def register_authentication(app):

    login_manager = LoginManager()
    login_manager.login_view = "/login/"
    login_manager.user_loader(load_user)
    login_manager.init_app(app)
    app.context_processor(lambda: dict(user=get_user()))

    @app.route("/login/", methods=["GET", "POST"])
    def login():
        """
        The login view
        """
        form = LoginForm()
        if form.validate_on_submit():
            login_user(load_user(user_id=1), remember=True)
            next_url = flask.request.args.get("next")
            return flask.redirect(next_url or "/")

        return flask.render_template("login.html", form=form)

    @app.route("/logout/")
    @login_required
    def logout():
        """
        The logout view
        """
        logout_user()
        return flask.redirect("/")
