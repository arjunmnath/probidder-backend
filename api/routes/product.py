from flask import request
from flask_restful import Resource
from api.models import db, Category, Product, ProductImage, CatProd, Bid
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api.routes import api
from sqlalchemy import func

# Resource for managing a single product
class ProductResource(Resource):
    def get(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400

        try:
            product = Product.query.get_or_404(product_id)
            product_data = {
                'productId': product.productId,
                'title': product.title,
                'description': product.description,
                'condition': product.condition,
                'initialBid': float(product.initialBid),
                'currentBidPrice': float(product.currentBidPrice),
                'status': product.status,
                'startTime': product.startTime.isoformat(),
                'endTime': product.endTime.isoformat(),
                'images': [{'imageURL': img.imageURL} for img in product.images]
            }
            return product_data
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400

        data = request.get_json()
        try:
            product = Product.query.get_or_404(product_id)
            
            # Update product details with provided values or keep existing ones
            product.title = data.get('title', product.title)
            product.description = data.get('description', product.description)
            product.condition = data.get('condition', product.condition)
            product.initialBid = data.get('initialBid', product.initialBid)
            product.status = data.get('status', product.status)
            product.startTime = data.get('startTime', product.startTime)
            product.endTime = data.get('endTime', product.endTime)

            # Update product images if provided
            images = data.get('images', [])
            if images:
                ProductImage.query.filter_by(productId=product.productId).delete()
                for image_url in images:
                    new_product_img = ProductImage(productId=product.productId, imageURL=image_url)
                    db.session.add(new_product_img)

            db.session.commit()
            return {'message': 'Product updated successfully'}, 200
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error updating product'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400

        try:
            product = Product.query.get_or_404(product_id)
            db.session.delete(product)
            db.session.commit()
            return {'message': 'Product deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

#Create new product
class ProductCreateResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_product = Product(
                title=data['title'],
                description=data['description'],
                condition=data['condition'],
                initialBid=data['initialBid'],
                status=data['status'],
                startTime=data['startTime'],
                endTime=data['endTime'],
                userId=data['userId']
            )
            
            categoryId = data['categoryId']
            category = Category.query.get_or_404(categoryId)

            db.session.add(new_product)
            db.session.commit()

            CatProd_entry = CatProd(categoryId=categoryId, productId=new_product.productId)
            db.session.add(CatProd_entry)
            db.session.commit()

            if 'images' in data:
                for image_url in data['images']:
                    new_product_img = ProductImage(productId=new_product.productId, imageURL=image_url)
                    db.session.add(new_product_img)
                db.session.commit()

            return {'message': 'Product created successfully'}, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error creating product'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

# Resource for listing products with optional filters
class ProductListResource(Resource):
    def get(self):
        status = request.args.get('status', None)
        sort_by = request.args.get('sort_by', 'startTime')
        sort_order = request.args.get('sort_order', 'asc')
        limit = request.args.get('limit', default=5, type=int)  # Convert limit to integer

        try:
            query = db.session.query(Product)
            
            if status:
                query = query.filter(Product.status == status)
            
            if sort_order == 'desc':
                query = query.order_by(getattr(Product, sort_by).desc())
            else:
                query = query.order_by(getattr(Product, sort_by).asc())

            if limit:
                query = query.limit(limit)
            
            products = query.all()
            products_list = [
                {
                    'productId': p.productId,
                    'title': p.title,
                    'description': p.description,
                    'condition': p.condition,
                    'initialBid': float(p.initialBid),
                    'currentBidPrice': float(p.currentBidPrice),
                    'status': p.status,
                    'startTime': p.startTime.isoformat(),
                    'endTime': p.endTime.isoformat(),
                    'images': [{'imageURL': img.imageURL} for img in p.images]
                } for p in products
            ]
            return products_list
        except Exception as e:
            return {'error': str(e)}, 500

# Resource for managing products by category
class CategoryProductsResource(Resource):
    def get(self):
        category_id = request.args.get('categoryId', None)
        status = request.args.get('status', 'active')
        sort_by = request.args.get('sortBy', 'startTime')
        sort_order = request.args.get('sortOrder', 'asc')
        limit = request.args.get('limit', default=5, type=int)  # Convert limit to integer

        if not category_id:
            return {'error': 'categoryId query parameter is required'}, 400

        try:
            query = db.session.query(Product).join(CatProd).filter(CatProd.categoryId == category_id)
            
            if status:
                query = query.filter(Product.status == status)
            
            if sort_by:
                column = getattr(Product, sort_by, None)
                if column is None:
                    return {'error': 'Invalid sortBy parameter'}, 400
                if sort_order == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

            if limit:
                query = query.limit(limit)
            
            products = query.all()
            products_list = [
                {
                    'productId': p.productId,
                    'title': p.title,
                    'description': p.description,
                    'condition': p.condition,
                    'initialBid': float(p.initialBid) if p.initialBid is not None else None,
                    'currentBidPrice': float(p.currentBidPrice) if p.currentBidPrice is not None else None,
                    'status': p.status,
                    'startTime': p.startTime.isoformat() if p.startTime else None,
                    'endTime': p.endTime.isoformat() if p.endTime else None,
                    'images': [{'imageURL': img.imageURL} for img in p.images]
                } for p in products
            ]

            return products_list
        except SQLAlchemyError as e:
            # Handle SQLAlchemy-specific exceptions
            return {'error': str(e)}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        
class TrendingProducts(Resource):
    def get(self):
        # Get the number of products to return from query parameters, default to 2
        num_products = request.args.get('limit', default=2, type=int)
        try:
            # Query to get products with the highest number of bids
            trending_products = (
                db.session.query(Product, func.count(Bid.bidId).label('bid_count'))
                .join(Bid, Product.productId == Bid.productId)
                .group_by(Product.productId)
                .order_by(func.count(Bid.bidId).desc())
                .limit(num_products)
                .all()
            )
            
            # Prepare the response
            response = []
            for product, bid_count in trending_products:
                response.append({
                    'productId': product.productId,
                    'title': product.title,
                    'description': product.description,
                    'bid_count': bid_count,
                    'currentBidPrice': float(product.currentBidPrice) if product.currentBidPrice is not None else None,
                    'condition': product.condition,
                    'status': product.status,
                    'startTime': product.startTime.isoformat() if product.startTime else None,
                    'endTime': product.endTime.isoformat() if product.endTime else None,
                    'userId': product.userId,
                    'images': [{'imageURL': img.imageURL} for img in product.images]
                })
            
            return response
        except SQLAlchemyError as e:
            # Handle SQLAlchemy-specific exceptions
            return {'error': str(e)}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500

# Register resources with the API
api.add_resource(ProductResource, '/api/v2/products/product')   #id
api.add_resource(ProductListResource, '/api/v2/products')   #status,limit for getting list of products of specified status
api.add_resource(ProductCreateResource, '/api/v2/products/create')    #POST for creating product
api.add_resource(CategoryProductsResource, '/api/v2/categories/products')   #categoryId, sortBy=currentBidPrice, sortOrder=desc (default asc)
api.add_resource(TrendingProducts, '/api/v2/products/trending')    #limit
