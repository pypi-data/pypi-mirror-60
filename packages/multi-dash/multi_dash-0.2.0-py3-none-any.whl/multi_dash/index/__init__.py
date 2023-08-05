import os

from flask import Flask, render_template, send_from_directory, Blueprint

dash_index = Blueprint(
    "multi-dash_index", __name__, template_folder="templates", static_folder="static"
)
