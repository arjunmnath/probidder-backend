from flask import Blueprint
from flask_restful import Api

appbp = Blueprint('appbp', __name__)

api = Api(appbp)

from api.routes import  bid, category, messages, order, product, review, user
