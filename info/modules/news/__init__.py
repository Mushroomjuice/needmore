from flask import Blueprint
# from main import app

news_blu = Blueprint("news",__name__,url_prefix="/news")

from .views import *