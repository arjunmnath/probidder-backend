from flask import request, jsonify
from flask_restful import Resource
from api.models import db, Messages
from sqlalchemy.exc import IntegrityError
from api.routes import api

# Resource for managing messages
class MessagesResource(Resource):
    def post(self):
        """Send a new message."""
        data = request.get_json()
        try:
            new_message = Messages(
                sentTime=data['sentTime'],
                readTime=data.get('readTime'),
                messageContent=data['messageContent'],
                productId=data.get('productId'),
                sellerId=data['sellerId'],
                receiverId=data['receiverId']
            )
            db.session.add(new_message)
            db.session.commit()
            return jsonify({'message': 'Message sent successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Invalid data'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class UserMessagesResource(Resource):
    def get(self, user_id):
        """Fetch all messages for a specific user (either sent or received)."""
        try:
            messages = Messages.query.filter(
                (Messages.sellerId == user_id) | (Messages.receiverId == user_id)
            ).all()
            messages_list = [
                {
                    'messageId': m.messageId,
                    'sentTime': m.sentTime.isoformat(),
                    'readTime': m.readTime.isoformat() if m.readTime else None,
                    'messageContent': m.messageContent,
                    'productId': m.productId,
                    'sellerId': m.sellerId,
                    'receiverId': m.receiverId
                } for m in messages
            ]
            return jsonify(messages_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class MessageResource(Resource):
    def get(self, message_id):
        """Fetch a single message by its ID."""
        try:
            message = Messages.query.get_or_404(message_id)
            message_data = {
                'messageId': message.messageId,
                'sentTime': message.sentTime.isoformat(),
                'readTime': message.readTime.isoformat() if message.readTime else None,
                'messageContent': message.messageContent,
                'productId': message.productId,
                'sellerId': message.sellerId,
                'receiverId': message.receiverId
            }
            return jsonify(message_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def put(self, message_id):
        """Update a message's read time or content."""
        data = request.get_json()
        try:
            message = Messages.query.get_or_404(message_id)
            message.readTime = data.get('readTime', message.readTime)
            message.messageContent = data.get('messageContent', message.messageContent)
            db.session.commit()
            return jsonify({'message': 'Message updated successfully'}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Invalid data'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def delete(self, message_id):
        """Delete a message by its ID."""
        try:
            message = Messages.query.get_or_404(message_id)
            db.session.delete(message)
            db.session.commit()
            return jsonify({'message': 'Message deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Register the resources with the API
api.add_resource(MessagesResource, '/api/v2/messages')
api.add_resource(UserMessagesResource, '/api/v2/users/<int:user_id>/messages')
api.add_resource(MessageResource, '/api/v2/messages/<int:message_id>')
