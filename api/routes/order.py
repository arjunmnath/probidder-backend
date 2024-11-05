from flask import request, jsonify
from flask_restful import Resource
from mysql.connector import Error
from models import create_connection
from routes import api

# Resource for managing user orders
class UserOrders(Resource):
    def get(self):

        user_id = request.args.get('userId', default=None, type=int)

        connection, cursor = None, None
        
        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM `Order` WHERE userId = %s", (user_id,)
            )
            orders = cursor.fetchall()
            # Format the orders' paymentTime and orderDate if necessary
            for order in orders:
                order['orderDate'] = order['orderDate'].isoformat() if order['orderDate'] else None
                order['paymentTime'] = order['paymentTime'].isoformat() if order['paymentTime'] else None
                order['totalAmount'] = float(order['totalAmount'])
            return orders, 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def post(self):
        user_id = request.args.get('userId')

        connection, cursor = None, None
        data = request.get_json()
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO `Order` (userId, orderDate, orderStatus, paymentTime, paymentStatus, paymentMethod, totalAmount, transactionId, productId) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, data['orderDate'], data['orderStatus'], data.get('paymentTime'), 
                 data['paymentStatus'], data['paymentMethod'], data['totalAmount'], 
                 data['transactionId'], data['productId'])
            )
            connection.commit()
            return {'message': 'Order created successfully'}, 201
        except Error as e:
            return {'error': str(e)}, 400
        finally:
            cursor.close()
            connection.close()

    def put(self):
        user_id = request.args.get('userId')
        order_id = request.args.get('orderId')

        connection, cursor = None, None
        data = request.get_json()
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE `Order` 
                SET orderStatus = %s, paymentTime = %s, paymentStatus = %s, 
                    paymentMethod = %s, totalAmount = %s, transactionId = %s, productId = %s 
                WHERE userId = %s AND orderId = %s
                """,
                (data.get('orderStatus'), data.get('paymentTime'), data.get('paymentStatus'),
                 data.get('paymentMethod'), data.get('totalAmount'), data.get('transactionId'),
                 user_id, order_id)
            )
            connection.commit()
            if cursor.rowcount == 0:
                return {'error': 'Order not found'}, 404
            
            return {'message': 'Order updated successfully'}, 200
        except Error as e:
            return {'error': str(e)}, 400
        finally:
            cursor.close()
            connection.close()

    def delete(self):
        user_id = request.args.get('userId')
        order_id = request.args.get('orderId')

        connection, cursor = None, None
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM `Order` WHERE userId = %s AND orderId = %s", (user_id, order_id)
            )
            connection.commit()
            if cursor.rowcount == 0:
                return {'error': 'Order not found'}, 404
            
            return {'message': 'Order deleted successfully'}, 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

# Register the resource with the API
api.add_resource(UserOrders, '/api/v2/users/orders')
