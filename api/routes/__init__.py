from flask import Blueprint
from flask_restful import Api

appbp = Blueprint('appbp', __name__)

api = Api(appbp)

from routes import  bid, category, order, product, user
