from flask import Blueprint
# from main import app

passport_blu = Blueprint("passport",__name__,url_prefix="/passport")

from .views import *