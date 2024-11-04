from flask import request, jsonify
from flask_restful import Resource
from api.models import db, Category
from sqlalchemy.exc import IntegrityError
from api.routes import api

class CategoryResource(Resource):
    def post(self):
        try:
            # Get JSON data from the request
            data = request.get_json()
            
            # Extract category name
            category_name = data['categoryName']
            
            # Check if the category already exists
            existing_category = Category.query.filter_by(categoryName=category_name).first()
            if existing_category:
                return {'message': 'Category already exists'}, 400
            
            # Create a new category instance
            new_category = Category(categoryName=category_name)
            
            # Add the new category to the database
            db.session.add(new_category)
            db.session.commit()
            
            # Return success response
            return {'message': 'Category added successfully', 'categoryId': new_category.categoryId}, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid data'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def get(self):
        try:
            # Fetch all categories from the database
            categories = Category.query.all()
            
            # Prepare response data
            categories_list = [
                {
                    'categoryId': c.categoryId,
                    'categoryName': c.categoryName
                } for c in categories
            ]
            
            return categories_list
        except Exception as e:
            return {'error': str(e)}, 500

class CategoryDetailResource(Resource):
    def get(self, category_id):
        try:
            # Fetch the category by ID
            category = Category.query.get_or_404(category_id)
            
            return {
                'categoryId': category.categoryId,
                'categoryName': category.categoryName
            }
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self, category_id):
        try:
            # Get JSON data from the request
            data = request.get_json()
            
            # Fetch the category by ID
            category = Category.query.get_or_404(category_id)
            
            # Update category name
            category.categoryName = data.get('categoryName', category.categoryName)
            
            # Commit the changes
            db.session.commit()
            
            return {'message': 'Category updated successfully'}
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid data'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self, category_id):
        try:
            # Fetch the category by ID
            category = Category.query.get_or_404(category_id)
            
            # Delete the category
            db.session.delete(category)
            db.session.commit()
            
            return {'message': 'Category deleted successfully'}
        except Exception as e:
            return {'error': str(e)}, 500

# Add the resources to the API
api.add_resource(CategoryResource, '/api/v2/categories')
api.add_resource(CategoryDetailResource, '/api/v2/categories/<int:category_id>')
