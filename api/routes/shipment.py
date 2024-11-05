from flask import request
from flask_restful import Resource
from mysql.connector import Error
from routes import api
from models import create_connection

class ShipmentResource(Resource):
    def get(self):
        shipment_id = request.args.get('shippingId')
        connection, cursor = None, None

        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            if shipment_id:
                cursor.execute(
                    "SELECT * FROM Shipment WHERE shippingId = %s", (shipment_id,)
                )
                shipment = cursor.fetchone()
                if shipment:
                    return [{
                        'shippingId': shipment['shippingId'],
                        'shippingMethod': shipment['shippingMethod'],
                        'trackingNumber': shipment['trackingNumber'],
                        'carrierName': shipment['carrierName'],
                        'shippingStatus': shipment['shippingStatus'],
                        'shippingCost': float(shipment['shippingCost']) if shipment['shippingCost'] is not None else None,
                        'estimatedDeliveryDate': shipment['estimatedDeliveryDate'].isoformat() if shipment['estimatedDeliveryDate'] else None,
                        'houseFlatNo': shipment['houseFlatNo'],
                        'street': shipment['street'],
                        'city': shipment['city'],
                        'pincode': shipment['pincode'],
                        'orderId': shipment['orderId']
                    }], 200
                else:
                    return {'error': 'Shipment not found'}, 404
            else:
                cursor.execute("SELECT * FROM Shipment")
                shipments = cursor.fetchall()
                result = [{
                    'shippingId': shipment['shippingId'],
                    'shippingMethod': shipment['shippingMethod'],
                    'trackingNumber': shipment['trackingNumber'],
                    'carrierName': shipment['carrierName'],
                    'shippingStatus': shipment['shippingStatus'],
                    'shippingCost': float(shipment['shippingCost']) if shipment['shippingCost'] is not None else None,
                    'estimatedDeliveryDate': shipment['estimatedDeliveryDate'].isoformat() if shipment['estimatedDeliveryDate'] else None,
                    'houseFlatNo': shipment['houseFlatNo'],
                    'street': shipment['street'],
                    'city': shipment['city'],
                    'pincode': shipment['pincode'],
                    'orderId': shipment['orderId']
                } for shipment in shipments]
                return result, 200
            
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def post(self):
        data = request.get_json()
        connection, cursor = None, None
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO Shipment (shippingMethod, trackingNumber, carrierName, shippingStatus, 
                                      shippingCost, estimatedDeliveryDate, houseFlatNo, street, city, pincode, orderId) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (data['shippingMethod'], data.get('trackingNumber'), data.get('carrierName'),
                 data['shippingStatus'], data.get('shippingCost'), data.get('estimatedDeliveryDate'),
                 data['houseFlatNo'], data['street'], data['city'], data['pincode'], data.get('orderId'))
            )
            connection.commit()
            return {'message': 'Shipment created successfully'}, 201
            
        except Error as e:
            return {'error': str(e)}, 400
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def put(self):
        shipment_id = request.args.get('shippingId', default=None, type=int)
        data = request.get_json()
        connection, cursor = None, None
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE Shipment 
                SET shippingMethod = %s, trackingNumber = %s, carrierName = %s, 
                    shippingStatus = %s, shippingCost = %s, estimatedDeliveryDate = %s,
                    houseFlatNo = %s, street = %s, city = %s, pincode = %s, orderId = %s 
                WHERE shippingId = %s
                """,
                (data['shippingMethod'], data.get('trackingNumber'), data.get('carrierName'),
                 data['shippingStatus'], data.get('shippingCost'), data.get('estimatedDeliveryDate'),
                 data['houseFlatNo'], data['street'], data['city'], data['pincode'], 
                 data.get('orderId'), shipment_id)
            )
            connection.commit()
            if cursor.rowcount == 0:
                return {'error': 'Shipment not found'}, 404
            
            return {'message': 'Shipment updated successfully'}, 200
            
        except Error as e:
            return {'error': str(e)}, 400
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete(self):
        shipment_id = request.args.get('shippingId', default=None, type=int)
        connection, cursor = None, None
        
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM Shipment WHERE shippingId = %s", (shipment_id,)
            )
            connection.commit()
            if cursor.rowcount == 0:
                return {'error': 'Shipment not found'}, 404
            
            return {'message': 'Shipment deleted successfully'}, 200
            
        except Error as e:
            return {'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Register the resource with the API
api.add_resource(ShipmentResource, '/api/v2/shipments')
