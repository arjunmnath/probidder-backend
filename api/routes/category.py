from flask import request, jsonify
from flask_restful import Resource
from mysql.connector import Error
from models import create_connection
from routes import api

class Category(Resource):
    def post(self):
        try:
            # Get JSON data from the request
            data = request.get_json()
            category_name = data.get('categoryName')

            if not category_name:
                return {'error': 'categoryName is required'}, 400
            
            # Check if the category already exists
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Category WHERE categoryName = %s", (category_name,))
            existing_category = cursor.fetchone()
            if existing_category:
                return {'message': 'Category already exists'}, 400
            
            # Insert a new category
            cursor.execute("INSERT INTO Category (categoryName) VALUES (%s)", (category_name,))
            connection.commit()
            return jsonify({'message': 'Category added successfully', 'categoryId': cursor.lastrowid}), 201
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def get(self):
        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Category")
            categories = cursor.fetchall()
            return jsonify(categories), 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

class CategoryDetail(Resource):
    def get(self):
        category_id = request.args.get('categoryId')
        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Category WHERE categoryId = %s", (category_id,))
            category = cursor.fetchone()
            if not category:
                return {'error': 'Category not found'}, 404
            return jsonify(category), 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def put(self):
        category_id = request.args.get('categoryId')
        try:
            data = request.get_json()
            category_name = data.get('categoryName')

            if not category_name:
                return {'error': 'categoryName is required'}, 400
            
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE Category SET categoryName = %s WHERE categoryId = %s", (category_name, category_id))
            connection.commit()

            if cursor.rowcount == 0:
                return {'error': 'Category not found'}, 404
            
            return {'message': 'Category updated successfully'}, 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def delete(self):
        category_id = request.args.get('categoryId')
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Category WHERE categoryId = %s", (category_id,))
            connection.commit()

            if cursor.rowcount == 0:
                return {'error': 'Category not found'}, 404
            
            return {'message': 'Category deleted successfully'}, 200
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

# Add the resources to the API
api.add_resource(Category, '/api/v2/categories')
api.add_resource(CategoryDetail, '/api/v2/category') #categoryId