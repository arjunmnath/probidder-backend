from flask import request
from flask_restful import Resource
from mysql.connector import Error
from routes import api
from models import create_connection

# Resource for managing a single product
class Product(Resource):
    def get(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400
        
        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute('SELECT * FROM Product WHERE productId = %s', (product_id,))
            product = cursor.fetchone()
            
            if not product:
                return {'error': 'Product not found'}, 404
            
            cursor.execute('SELECT imageURL FROM Product_img WHERE productId = %s', (product_id,))
            images = cursor.fetchall()
            product['images'] = [{'imageURL': img['imageURL']} for img in images]
            
            return [{
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'condition': product['condition'],
                    'initialBid': float(product['initialBid']),
                    'currentBidPrice': float(product['currentBidPrice']),
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat(),
                    'endTime': product['endTime'].isoformat(),
                    'images': product['images']
                }]
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

    def put(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400

        data = request.get_json()

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Update the product details
            update_query = '''
            UPDATE Product 
            SET title = %s, description = %s, condition = %s, initialBid = %s, status = %s, startTime = %s, endTime = %s
            WHERE productId = %s
            '''
            cursor.execute(update_query, (
                data.get('title'),
                data.get('description'),
                data.get('condition'),
                data.get('initialBid'),
                data.get('status'),
                data.get('startTime'),
                data.get('endTime'),
                product_id
            ))

            # Delete existing images and add new ones
            if 'images' in data:
                cursor.execute('DELETE FROM Product_img WHERE productId = %s', (product_id,))
                for image_url in data['images']:
                    cursor.execute('INSERT INTO Product_img (productId, imageURL) VALUES (%s, %s)', (product_id, image_url))

            conn.commit()
            return {'message': 'Product updated successfully'}, 200
        except Error as e:
            conn.rollback()
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

    def delete(self):
        product_id = request.args.get('id')
        if not product_id:
            return {'error': 'Product ID is required'}, 400

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM Product WHERE productId = %s', (product_id,))
            conn.commit()

            return {'message': 'Product deleted successfully'}, 200
        except Error as e:
            conn.rollback()
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

#Create new product
class ProductCreate(Resource):
    def post(self):
        data = request.get_json()

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Insert product
            insert_product_query = '''
            INSERT INTO Product (title, description, condition, initialBid, status, startTime, endTime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_product_query, (
                data['title'], data['description'], data['condition'], data['initialBid'],
                data['status'], data['startTime'], data['endTime']
            ))
            new_product_id = cursor.lastrowid

            # Insert into CatProd
            insert_catprod_query = 'INSERT INTO Cat_Prod (categoryId, productId) VALUES (%s, %s)'
            cursor.execute(insert_catprod_query, (data['categoryId'], new_product_id))

            # Insert product images if provided
            if 'images' in data:
                for image_url in data['images']:
                    insert_image_query = 'INSERT INTO Product_img (productId, imageURL) VALUES (%s, %s)'
                    cursor.execute(insert_image_query, (new_product_id, image_url))

            conn.commit()
            return {'message': 'Product created successfully'}, 201
        except Error as e:
            conn.rollback()
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

# Resource for listing products with optional filters
class ProductList(Resource):
    def get(self):
        status = request.args.get('status', None)
        sort_by = request.args.get('sort_by', 'startTime')
        sort_order = request.args.get('sort_order', 'asc')
        limit = request.args.get('limit', default=5, type=int)  # Convert limit to integer
        
        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Build the base SQL query
            query = "SELECT * FROM Product"
            params = []

            # Apply status filter if provided
            if status:
                query += " WHERE status = %s"
                params.append(status)

            # Apply sorting
            query += f" ORDER BY {sort_by} {sort_order.upper()}"

            # Apply limit
            query += " LIMIT %s"
            params.append(limit)

            # Execute the query
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            # Fetch product images for each product
            products_list = []
            for product in products:
                cursor.execute("SELECT imageURL FROM Product_img WHERE productId = %s", (product['productId'],))
                images = cursor.fetchall()
                product['images'] = [{'imageURL': img['imageURL']} for img in images]
                products_list.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'condition': product['condition'],
                    'initialBid': float(product['initialBid']),
                    'currentBidPrice': float(product['currentBidPrice']),
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat(),
                    'endTime': product['endTime'].isoformat(),
                    'images': product['images']
                })

            return products_list
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

# Allowed sort fields and order for safety
ALLOWED_SORT_FIELDS = {'startTime', 'endTime', 'title'}
ALLOWED_SORT_ORDERS = {'asc', 'desc'}

class CategoryProducts(Resource):
    def get(self):
        category_id = request.args.get('categoryId', default=None, type=int)
        status = request.args.get('status', 'live')
        sort_by = request.args.get('sortBy', 'startTime')
        sort_order = request.args.get('sortOrder', 'asc')
        limit = request.args.get('limit', default=5, type=int)  # Convert limit to integer
        offset = request.args.get('offset', default=None, type=int)

        if not category_id:
            return {'error': 'categoryId query parameter is required'}, 400

        if sort_by not in ALLOWED_SORT_FIELDS:
            return {'error': f"Invalid sortBy parameter. Allowed values are {', '.join(ALLOWED_SORT_FIELDS)}"}, 400
        
        if sort_order.lower() not in ALLOWED_SORT_ORDERS:
            return {'error': f"Invalid sortOrder parameter. Allowed values are {', '.join(ALLOWED_SORT_ORDERS)}"}, 400

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Base SQL query for fetching products in a category
            query = """
                SELECT p.* 
                FROM Product p
                JOIN Cat_Prod cp ON p.productId = cp.productId
                WHERE cp.categoryId = %s
            """
            params = [category_id]

            # Add status filter if provided
            if status:
                query += " AND p.status = %s"
                params.append(status)

            # Apply sorting with validated parameters
            query += f" ORDER BY {sort_by} {sort_order.upper()}"

            # Apply limit
            query += " LIMIT %s"
            params.append(limit)

            if offset:
                query += " OFFSET %s"
                params.append(offset)

            # Debug: Print the final SQL query and parameters
            print(f"Executing Query: {query} with params: {params}")

            # Execute the query
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            # Debug: Check fetched products
            print(f"Fetched Products: {products}")

            # Check if products are found
            if not products:
                return {'message': 'No products found for the specified category'}, 404

            # Fetch product images for each product
            products_list = []
            
            for product in products:
                # Corrected method call
                product['images'] = self.fetch_product_images(cursor, product['productId'])
                
                products_list.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'condition': product['condition'],
                    'initialBid': float(product['initialBid']) if product['initialBid'] is not None else None,
                    'currentBidPrice': float(product['currentBidPrice']) if product['currentBidPrice'] is not None else None,
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat() if product['startTime'] else None,
                    'endTime': product['endTime'].isoformat() if product['endTime'] else None,
                    'images': product['images']
                })

            return products_list, 200

        except Error as e:
            return {'error': str(e)}, 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_product_images(self, cursor, product_id):
        cursor.execute("SELECT imageURL FROM Product_img WHERE productId = %s", (product_id,))
        images = cursor.fetchall()
        return [{'imageURL': img['imageURL']} for img in images]
                  
class TrendingProducts(Resource):
    def get(self):
        # Get the number of products to return from query parameters, default to 2
        num_products = request.args.get('limit', default=5, type=int)

        conn, cursor = None, None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # SQL query to get products with the highest number of bids
            query = """
                SELECT p.*, COUNT(b.bidId) AS bid_count
                FROM Product p
                JOIN Bid b ON p.productId = b.productId
                GROUP BY p.productId
                ORDER BY bid_count DESC
                LIMIT %s
            """

            # Execute the query with the limit parameter
            cursor.execute(query, (num_products,))
            trending_products = cursor.fetchall()

            # Prepare the response
            response = []
            for product in trending_products:
                cursor.execute("SELECT imageURL FROM Product_img WHERE productId = %s", (product['productId'],))
                images = cursor.fetchall()

                response.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'bid_count': product['bid_count'],
                    'currentBidPrice': float(product['currentBidPrice']) if product['currentBidPrice'] is not None else None,
                    'condition': product['condition'],
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat() if product['startTime'] else None,
                    'endTime': product['endTime'].isoformat() if product['endTime'] else None,
                    'images': [{'imageURL': img['imageURL']} for img in images]
                })

            return response
        except Error as e:
            # Handle MySQL-specific exceptions
            return {'error': str(e)}, 500
        except Exception as e:
            # Handle general exceptions
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            conn.close()

class LHTProducts(Resource):
    def get(self):

        conn, cursor = None, None  # Initialize outside try block
        try:
            conn = create_connection()  # Create connection
            cursor = conn.cursor(dictionary=True)  # Create cursor

            # Prepare the response
            response = []

            # Helper function to fetch images for a product
            def fetch_images(product_id):
                cursor.execute("SELECT imageURL FROM Product_img WHERE productId = %s", (product_id,))
                return [{'imageURL': img['imageURL']} for img in cursor.fetchall()]

            # Fetch Trending Products
            trending_query = """
                SELECT p.*, COUNT(b.bidId) AS bid_count
                FROM Product p
                LEFT JOIN Bid b ON p.productId = b.productId
                GROUP BY p.productId
                ORDER BY bid_count DESC
                LIMIT 10
            """
            cursor.execute(trending_query)
            trending_products = cursor.fetchall()

            trending_sub = []
            for product in trending_products:
                images = fetch_images(product['productId'])
                trending_sub.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'bid_count': product['bid_count'],
                    'currentBidPrice': float(product['currentBidPrice']) if product['currentBidPrice'] is not None else None,
                    'condition': product['condition'],
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat() if product['startTime'] else None,
                    'endTime': product['endTime'].isoformat() if product['endTime'] else None,
                    'images': images
                })

            response.append({'trending': trending_sub})

            # Fetch Products with Highest Bids
            high_bid_query = """
                SELECT p.*, MAX(b.bidAmount) AS highest_bid
                FROM Product p
                LEFT JOIN Bid b ON p.productId = b.productId
                GROUP BY p.productId
                ORDER BY highest_bid DESC
                LIMIT 8
            """
            cursor.execute(high_bid_query)
            high_bid_products = cursor.fetchall()

            high_bid_sub = []
            for product in high_bid_products:
                images = fetch_images(product['productId'])
                high_bid_sub.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'highest_bid': float(product['highest_bid']) if product['highest_bid'] is not None else None,
                    'currentBidPrice': float(product['currentBidPrice']) if product['currentBidPrice'] is not None else None,
                    'condition': product['condition'],
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat() if product['startTime'] else None,
                    'endTime': product['endTime'].isoformat() if product['endTime'] else None,
                    'images': images
                })

            response.append({'highBids': high_bid_sub})

            # Fetch Live Auctions
            live_auction_query = """
                SELECT *
                FROM Product
                WHERE status = 'live'
                ORDER BY startTime
                LIMIT 10
            """
            cursor.execute(live_auction_query)
            live_auction_products = cursor.fetchall()

            live_sub = []
            for product in live_auction_products:
                images = fetch_images(product['productId'])
                live_sub.append({
                    'productId': product['productId'],
                    'title': product['title'],
                    'description': product['description'],
                    'currentBidPrice': float(product['currentBidPrice']) if product['currentBidPrice'] is not None else None,
                    'condition': product['condition'],
                    'status': product['status'],
                    'startTime': product['startTime'].isoformat() if product['startTime'] else None,
                    'endTime': product['endTime'].isoformat() if product['endTime'] else None,
                    'images': images
                })

            response.append({'live': live_sub})

            return response, 200

        except Error as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # Ensure cursor and connection are closed if they were created
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Register resources with the API
api.add_resource(Product, '/api/v2/products/product')   #id
api.add_resource(ProductList, '/api/v2/products')   #status,limit for getting list of products of specified status
api.add_resource(ProductCreate, '/api/v2/products/create')    #POST for creating product
api.add_resource(CategoryProducts, '/api/v2/categories/products')   #categoryId, sortBy=currentBidPrice, sortOrder=desc (default asc)
                                                                            #limit, status
api.add_resource(TrendingProducts, '/api/v2/products/trending')    #limit
api.add_resource(LHTProducts, '/api/products/lht')
