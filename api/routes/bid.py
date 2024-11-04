from flask import request, jsonify
from flask_restful import Resource
from api.models import db, Bid
from sqlalchemy.exc import IntegrityError
from api.routes import api

# Create an instance of Api


class BidResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_bid = Bid(
                bidAmount=data['bidAmount'],
                bidTime=data['bidTime'],
                userId=data['userId'],
                productId=data['productId']
            )
            db.session.add(new_bid)
            db.session.commit()
            return {'message': 'Bid placed successfully', 'bidId': new_bid.bidId}, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid data'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

class BidDetailResource(Resource):
    def get(self, bid_id):
        try:
            bid = Bid.query.get_or_404(bid_id)
            return {
                'bidId': bid.bidId,
                'bidAmount': float(bid.bidAmount),
                'bidTime': bid.bidTime.isoformat(),
                'isWinningBid': bid.isWinningBid,
                'userId': bid.userId,
                'productId': bid.productId
            }
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self, bid_id):
        try:
            bid = Bid.query.get_or_404(bid_id)
            db.session.delete(bid)
            db.session.commit()
            return {'message': 'Bid deleted successfully'}
        except Exception as e:
            return {'error': str(e)}, 500

class ProductBidsResource(Resource):
    def get(self, product_id):
        try:
            bids = Bid.query.filter_by(productId=product_id).all()
            bids_list = [
                {
                    'bidId': b.bidId,
                    'bidAmount': float(b.bidAmount),
                    'bidTime': b.bidTime.isoformat(),
                    'isWinningBid': b.isWinningBid,
                    'userId': b.userId
                } for b in bids
            ]
            return bids_list
        except Exception as e:
            return {'error': str(e)}, 500

class UserBidsResource(Resource):
    def get(self, user_id):
        try:
            bids = Bid.query.filter_by(userId=user_id).all()
            bids_list = [
                {
                    'bidId': b.bidId,
                    'bidAmount': float(b.bidAmount),
                    'bidTime': b.bidTime.isoformat(),
                    'isWinningBid': b.isWinningBid,
                    'productId': b.productId
                } for b in bids
            ]
            return bids_list
        except Exception as e:
            return {'error': str(e)}, 500

# Add the resources to the API
api.add_resource(BidResource, '/api/v2/bids')
api.add_resource(BidDetailResource, '/api/v2/bids/<int:bid_id>')
api.add_resource(ProductBidsResource, '/api/v2/products/<int:product_id>/bids')
api.add_resource(UserBidsResource, '/api/v2/users/<int:user_id>/bids')
