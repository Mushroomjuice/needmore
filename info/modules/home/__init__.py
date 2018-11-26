from flask import Blueprint
# from main import app

home_blu = Blueprint("home",__name__)

from .views import *
