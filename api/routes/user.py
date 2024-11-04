from flask import request, jsonify
from flask_restful import Resource
from api.models import db, User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from api.routes import api

# User Registration Resource
class UserRegistration(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data['username']
            email = data['email']
            password = data['password']

            # Check if username or email already exists
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                return {'error': 'Username or email already exists'}, 400

            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Create a new user instance
            new_user = User(
                username=username,
                phone=data['phone'],
                email=email,
                passwdHash=hashed_password,
                firstName=data['firstName'],
                lastName=data['lastName'],
                houseFlatNo=data['houseFlatNo'],
                street=data['street'],
                city=data['city'],
                pincode=data['pincode'],
                dateJoined=data['dateJoined'],
                isVerified=data['isVerified']
            )

            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'User registered successfully', 'userId': new_user.userId}, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error creating user'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

# User Login Resource
class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data['email']
            password = data['password']

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.passwdHash, password):
                return {'message': 'Login successful', 'userId': user.userId}, 200
            return {'error': 'Invalid credentials'}, 401
        except Exception as e:
            return {'error': str(e)}, 500

# User Details Resource
class UserDetails(Resource):
    def get(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            user_details = {
                'userId': user.userId,
                'username': user.username,
                'phone': user.phone,
                'email': user.email,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'houseFlatNo': user.houseFlatNo,
                'street': user.street,
                'city': user.city,
                'pincode': user.pincode,
                'dateJoined': user.dateJoined.isoformat(),
                'isVerified': user.isVerified
            }
            return user_details, 200
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self, user_id):
        try:
            data = request.get_json()
            user = User.query.get_or_404(user_id)

            # Update user details
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)

            # Check if username or email already exists
            if User.query.filter_by(username=user.username).first() or User.query.filter_by(email=user.email).first():
                return {'error': 'Username or email already exists'}, 400

            user.phone = data.get('phone', user.phone)
            user.firstName = data.get('firstName', user.firstName)
            user.lastName = data.get('lastName', user.lastName)
            user.houseFlatNo = data.get('houseFlatNo', user.houseFlatNo)
            user.street = data.get('street', user.street)
            user.city = data.get('city', user.city)
            user.pincode = data.get('pincode', user.pincode)
            user.dateJoined = data.get('dateJoined', user.dateJoined)
            user.isVerified = data.get('isVerified', user.isVerified)

            db.session.commit()

            return {'message': 'User details updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

# Register Resources with Flask-RESTful
api.add_resource(UserRegistration, '/api/v2/register')
api.add_resource(UserLogin, '/api/v2/login')
api.add_resource(UserDetails, '/api/v2/users/<int:user_id>')
