from flask import Blueprint, render_template

frontend = Blueprint('', __name__, template_folder='templates')

@frontend.route('/')
def home():
    return render_template("home.html")