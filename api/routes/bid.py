from flask import request, jsonify
from flask_restful import Resource
from mysql.connector import Error
from models import create_connection
from routes import api

class Bid(Resource):
    def post(self):
        connection, cursor = None, None
        try:
            # Parse the incoming JSON data
            data = request.get_json()

            # Validate input data
            required_fields = ['bidAmount', 'bidTime', 'isWinningBid', 'userId', 'productId']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Check data types
            if not isinstance(data['bidAmount'], (int, float)):
                return {'error': 'bidAmount must be a number'}, 400
            if not isinstance(data['isWinningBid'], bool):
                return {'error': 'isWinningBid must be a boolean'}, 400
            
            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor()

            # Prepare the insert query
            insert_query = """
            INSERT INTO Bid (bidAmount, bidTime, isWinningBid, userId, productId)
            VALUES (%s, %s, %s, %s, %s)
            """
            bid_values = (
                data['bidAmount'],
                data['bidTime'],  # Ensure that this is in the correct format (e.g., 'YYYY-MM-DD HH:MM:SS')
                data['isWinningBid'],
                data['userId'],
                data['productId']
            )
            
            # Execute the query
            cursor.execute(insert_query, bid_values)
            connection.commit()

            # Get the ID of the newly created bid
            bid_id = cursor.lastrowid
            
            return {
                'message': 'Bid placed successfully',
                'bidId': bid_id,
                'bidAmount': data['bidAmount'],
                'bidTime': data['bidTime'],
                'isWinningBid': data['isWinningBid'],
                'userId': data['userId'],
                'productId': data['productId']
            }, 201

        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

class BidDetail(Resource):
    def get(self):
        bid_id = request.args.get('bidId')

        connection, cursor = None, None
        try:
            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)  # Use dictionary for easier access to columns
            
            # Prepare the select query
            select_query = "SELECT * FROM Bid WHERE bidId = %s"
            cursor.execute(select_query, (bid_id,))
            bid = cursor.fetchone()  # Fetch one result
            
            if not bid:
                return {'error': 'Bid not found'}, 404
            
            return {
                'bidId': bid['bidId'],
                'bidAmount': float(bid['bidAmount']),
                'bidTime': bid['bidTime'].isoformat() if bid['bidTime'] else None,  # Handle None case
                'isWinningBid': bid['isWinningBid'],
                'userId': bid['userId'],
                'productId': bid['productId']
            }
        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete(self):
        bid_id = request.args.get('bidId')
        connection, cursor = None, None
        try:
            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor()

            # Prepare the delete query
            delete_query = "DELETE FROM Bid WHERE bidId = %s"
            cursor.execute(delete_query, (bid_id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return {'error': 'Bid not found'}, 404
            
            return {'message': 'Bid deleted successfully'}
        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

class ProductBids(Resource):
    def get(self):
        product_id = request.args.get('productId')
        connection, cursor = None, None
        try:
            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)  # Use dictionary for easier access to columns
            
            # Prepare the select query
            select_query = "SELECT * FROM Bid WHERE productId = %s"
            cursor.execute(select_query, (product_id,))
            bids = cursor.fetchall()  # Fetch all results
            
            # Prepare the response
            bids_list = [
                {
                    'bidId': bid['bidId'],
                    'bidAmount': float(bid['bidAmount']),
                    'bidTime': bid['bidTime'].isoformat() if bid['bidTime'] else None,  # Handle None case
                    'isWinningBid': bid['isWinningBid'],
                    'userId': bid['userId']
                } for bid in bids
            ]
            
            return bids_list if bids_list else [], 200  # Return an empty list if no bids found
        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

class UserBids(Resource):
    def get(self):
        user_id = request.args.get('userId')
        if not user_id:
            return {'error': 'Product ID is required'}, 400
        
        connection, cursor = None, None
        try:

            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)  # Use dictionary for easier access to columns
            
            # Prepare the select query
            select_query = "SELECT * FROM Bid WHERE userId = %s"
            cursor.execute(select_query, (user_id,))
            bids = cursor.fetchall()  # Fetch all results
            
            # Prepare the response
            bids_list = [
                {
                    'bidId': bid['bidId'],
                    'bidAmount': float(bid['bidAmount']),
                    'bidTime': bid['bidTime'].isoformat() if bid['bidTime'] else None,  # Handle None case
                    'isWinningBid': bid['isWinningBid'],
                    'productId': bid['productId']
                } for bid in bids
            ]
            
            return bids_list if bids_list else [], 200  # Return an empty list if no bids found
        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

class ProductHighestBid(Resource):
    def get(self):
        product_id = request.args.get('productId')

        connection, cursor = None, None
        try:
            # Establish database connection
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)  # Use dictionary for easier access to columns
            
            # Prepare the select query
            select_query = """
                SELECT * 
                FROM Bid 
                WHERE productId = %s
                ORDER BY bidAmount DESC
                LIMIT 1
            """
            cursor.execute(select_query, (product_id,))
            bids = cursor.fetchall()  # Fetch all results
            
            # Prepare the response
            bids_list = [
                {
                    'bidId': bid['bidId'],
                    'bidAmount': float(bid['bidAmount']),
                    'bidTime': bid['bidTime'].isoformat() if bid['bidTime'] else None,  # Handle None case
                    'isWinningBid': bid['isWinningBid'],
                    'userId': bid['userId']
                } for bid in bids
            ]
            
            return bids_list if bids_list else [], 200  # Return an empty list if no bids found
        except Error as err:
            # Handle MySQL-specific errors
            return {'error': f'MySQL error: {str(err)}'}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Add the resources to the API
api.add_resource(Bid, '/api/v2/bid')
api.add_resource(BidDetail, '/api/v2/bids')
api.add_resource(ProductBids, '/api/v2/product/bids') #productId
api.add_resource(UserBids, '/api/v2/users/bids') #userId
api.add_resource(ProductHighestBid, '/api/v2/product/highestbid') #productId