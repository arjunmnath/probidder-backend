from flask import request, jsonify
from flask_restful import Resource
from api.models import db, Order
from sqlalchemy.exc import IntegrityError
from api.routes import api

# Resource for managing user orders
class UserOrdersResource(Resource):
    def get(self, user_id):
        """Fetch all orders for a specific user."""
        try:
            orders = Order.query.filter_by(userId=user_id).all()
            orders_list = [
                {
                    'orderId': o.orderId,
                    'orderDate': o.orderDate.isoformat(),
                    'orderStatus': o.orderStatus,
                    'paymentTime': o.paymentTime.isoformat() if o.paymentTime else None,
                    'paymentStatus': o.paymentStatus,
                    'paymentMethod': o.paymentMethod,
                    'totalAmount': float(o.totalAmount),
                    'transactionId': o.transactionId,
                    'productId': o.productId
                } for o in orders
            ]
            return jsonify(orders_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def post(self, user_id):
        """Create a new order for a specific user."""
        data = request.get_json()
        try:
            new_order = Order(
                userId=user_id,
                orderDate=data['orderDate'],
                orderStatus=data['orderStatus'],
                paymentTime=data.get('paymentTime'),
                paymentStatus=data['paymentStatus'],
                paymentMethod=data['paymentMethod'],
                totalAmount=data['totalAmount'],
                transactionId=data['transactionId'],
                productId=data['productId']
            )
            db.session.add(new_order)
            db.session.commit()
            return jsonify({'message': 'Order created successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Error creating order'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def put(self, user_id, order_id):
        """Update an existing order for a specific user."""
        data = request.get_json()
        try:
            order = Order.query.filter_by(userId=user_id, orderId=order_id).first_or_404()
            order.orderStatus = data.get('orderStatus', order.orderStatus)
            order.paymentTime = data.get('paymentTime', order.paymentTime)
            order.paymentStatus = data.get('paymentStatus', order.paymentStatus)
            order.paymentMethod = data.get('paymentMethod', order.paymentMethod)
            order.totalAmount = data.get('totalAmount', order.totalAmount)
            order.transactionId = data.get('transactionId', order.transactionId)
            order.productId = data.get('productId', order.productId)
            db.session.commit()
            return jsonify({'message': 'Order updated successfully'}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Error updating order'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def delete(self, user_id, order_id):
        """Delete an order for a specific user."""
        try:
            order = Order.query.filter_by(userId=user_id, orderId=order_id).first_or_404()
            db.session.delete(order)
            db.session.commit()
            return jsonify({'message': 'Order deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Register the resource with the API
api.add_resource(UserOrdersResource, '/api/v2/users/<int:user_id>/orders', '/api/users/<int:user_id>/orders/<int:order_id>')
