from flask import request, jsonify
from flask_restful import Resource
from api.models import db, Review
from sqlalchemy.exc import IntegrityError
from api.routes import api

# Review Resource
class ReviewResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_review = Review(
                rating=data['rating'],
                comment=data['comment'],
                reviewDate=data['reviewDate'],
                productId=data['productId'],
                userId=data['userId']
            )
            db.session.add(new_review)
            db.session.commit()
            return {'message': 'Review added successfully'}, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid data'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self, review_id):
        data = request.get_json()
        try:
            review = Review.query.get_or_404(review_id)
            review.rating = data.get('rating', review.rating)
            review.comment = data.get('comment', review.comment)
            review.reviewDate = data.get('reviewDate', review.reviewDate)

            db.session.commit()
            return {'message': 'Review updated successfully'}, 200
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid data'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self, review_id):
        try:
            review = Review.query.get_or_404(review_id)
            db.session.delete(review)
            db.session.commit()
            return {'message': 'Review deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

# Product Reviews Resource
class ProductReviewsResource(Resource):
    def get(self, product_id):
        try:
            reviews = Review.query.filter_by(productId=product_id).all()
            reviews_list = [
                {
                    'reviewId': r.reviewId,
                    'rating': r.rating,
                    'comment': r.comment,
                    'reviewDate': r.reviewDate.isoformat(),
                    'userId': r.userId
                } for r in reviews
            ]
            return jsonify(reviews_list)
        except Exception as e:
            return {'error': str(e)}, 500

# Register Resources with Flask-RESTful
api.add_resource(ReviewResource, '/api/v2/reviews', '/api/reviews/<int:review_id>')
api.add_resource(ProductReviewsResource, '/api/v2/products/<int:product_id>/reviews')
