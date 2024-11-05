from flask import request, jsonify
from flask_restful import Resource
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from models import create_connection
from routes import api
from datetime import datetime

# User Registration Resource
class UserRegistration(Resource):
    def post(self):
        conn, cursor = None, None
        
        try:
            data = request.get_json()
            username = data['username']
            email = data['email']
            password = data['password']

            conn = create_connection()
            cursor = conn.cursor()
            # Check if username or email already exists
            cursor.execute("SELECT userId FROM User WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return {'error': 'Username or email already exists'}, 400

            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Create a new user instance
            cursor.execute(
                """
                INSERT INTO User (username, phone, email, passwdHash, firstName, lastName, 
                                   houseFlatNo, street, city, pincode, dateJoined, isVerified) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (username, data['phone'], email, hashed_password, data['firstName'], data['lastName'],
                 data['houseFlatNo'], data['street'], data['city'], data['pincode'], data['dateJoined'], data['isVerified'])
            )
            conn.commit()

            # Get the userId of the newly created user
            new_user_id = cursor.lastrowid
            return {'message': 'User registered successfully', 'userId': new_user_id}, 201
        except Error as e:
            return {'error': str(e)}, 400
        finally:
            cursor.close()
            conn.close()

# User Login Resource
class UserLogin(Resource):
    def post(self):
        conn, cursor = None, None
        
        try:
            data = request.get_json()
            email = data['email']
            password = data['password']

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT userId, passwdHash FROM User WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                return {'message': 'Login successful', 'userId': user[0]}, 200
            return {'error': 'Invalid credentials'}, 401
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

# Resource for managing user details
class UserDetails(Resource):
    def get(self):
        user_id = request.args.get('userId')
        if not user_id:
            return {'error': 'User ID is required'}, 400
        
        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM User WHERE userId = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return {'error': 'User not found'}, 404
            
            # Format the dateJoined if it's a datetime object
            date_joined = user['dateJoined']
            if isinstance(date_joined, str):
                date_joined = datetime.fromisoformat(date_joined)

            user_details = {
                'userId': user['userId'],
                'username': user['username'],
                'phone': user['phone'],
                'email': user['email'],
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'houseFlatNo': user['houseFlatNo'],
                'street': user['street'],
                'city': user['city'],
                'pincode': user['pincode'],
                'dateJoined': date_joined.isoformat() if isinstance(date_joined, datetime) else None,
                'isVerified': user['isVerified']
            }
            return user_details, 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def put(self):
        user_id = request.args.get('userId')
        if not user_id:
            return {'error': 'User ID is required'}, 400

        data = request.get_json()

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT userId FROM User WHERE userId = %s", (user_id,))
            if cursor.fetchone() is None:
                return {'error': 'User not found'}, 404
            
            # Update user details
            username = data.get('username')
            email = data.get('email')

            # Check if username or email already exists
            cursor.execute("SELECT userId FROM User WHERE (username = %s OR email = %s) AND userId != %s",
                           (username, email, user_id))
            if cursor.fetchone():
                return {'error': 'Username or email already exists'}, 400
            
            update_query = '''
            UPDATE User 
            SET username = %s, email = %s, phone = %s, firstName = %s, lastName = %s, 
                houseFlatNo = %s, street = %s, city = %s, pincode = %s, 
                isVerified = %s 
            WHERE userId = %s
            '''
            cursor.execute(update_query, (
                username,
                email,
                data.get('phone'),
                data.get('firstName'),
                data.get('lastName'),
                data.get('houseFlatNo'),
                data.get('street'),
                data.get('city'),
                data.get('pincode'),
                data.get('isVerified'),
                user_id
            ))

            conn.commit()
            return {'message': 'User details updated successfully'}, 200
        except Error as e:
            conn.rollback()
            return {'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete(self):
        user_id = request.args.get('userId')
        if not user_id:
            return {'error': 'User ID is required'}, 400

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Check if user exists before deletion
            cursor.execute("SELECT userId FROM User WHERE userId = %s", (user_id,))
            if cursor.fetchone() is None:
                return {'error': 'User not found'}, 404

            cursor.execute("DELETE FROM User WHERE userId = %s", (user_id,))
            conn.commit()

            return {'message': 'User deleted successfully'}, 200
        except Error as e:
            conn.rollback()
            return {'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Register Resources with Flask-RESTful
api.add_resource(UserRegistration, '/api/v2/register')
api.add_resource(UserLogin, '/api/v2/login')
api.add_resource(UserDetails, '/api/v2/users') #userId
