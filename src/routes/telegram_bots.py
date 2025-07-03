from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User
from src.models.telegram_bot import TelegramBot
import requests

telegram_bots_bp = Blueprint('telegram_bots', __name__)

def validate_telegram_bot(bot_token, chat_id):
    """Validate Telegram bot token and chat access"""
    try:
        # Test bot token by getting bot info
        bot_info_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(bot_info_url, timeout=10)
        
        if response.status_code != 200:
            return False, "Invalid bot token"
        
        bot_data = response.json()
        if not bot_data.get('ok'):
            return False, "Invalid bot token"
        
        bot_username = bot_data['result']['username']
        
        # Test chat access by getting chat info
        chat_info_url = f"https://api.telegram.org/bot{bot_token}/getChat"
        chat_response = requests.get(chat_info_url, params={'chat_id': chat_id}, timeout=10)
        
        if chat_response.status_code != 200:
            return False, "Cannot access chat. Make sure the bot is added to the channel/group as admin"
        
        chat_data = chat_response.json()
        if not chat_data.get('ok'):
            return False, "Cannot access chat. Make sure the bot is added to the channel/group as admin"
        
        chat_info = chat_data['result']
        chat_name = chat_info.get('title', 'Unknown')
        chat_type = chat_info.get('type', 'unknown')
        
        return True, {
            'bot_username': bot_username,
            'chat_name': chat_name,
            'chat_type': chat_type
        }
        
    except requests.RequestException:
        return False, "Failed to connect to Telegram API"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

@telegram_bots_bp.route('/telegram-bots', methods=['GET'])
@jwt_required()
def get_telegram_bots():
    try:
        current_user_id = get_jwt_identity()
        
        bots = TelegramBot.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'bots': [bot.to_dict() for bot in bots]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get bots', 'details': str(e)}), 500

@telegram_bots_bp.route('/telegram-bots', methods=['POST'])
@jwt_required()
def create_telegram_bot():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('bot_token', 'chat_id')):
            return jsonify({'error': 'Bot token and chat ID are required'}), 400
        
        bot_token = data['bot_token'].strip()
        chat_id = data['chat_id'].strip()
        is_private = data.get('is_private', False)
        
        # Validate bot token and chat access
        is_valid, result = validate_telegram_bot(bot_token, chat_id)
        if not is_valid:
            return jsonify({'error': result}), 400
        
        # Check if bot already exists for this user
        existing_bot = TelegramBot.query.filter_by(
            user_id=current_user_id,
            chat_id=chat_id
        ).first()
        
        if existing_bot:
            return jsonify({'error': 'Bot for this chat already exists'}), 409
        
        # Create new bot
        bot = TelegramBot(
            user_id=current_user_id,
            bot_token=bot_token,
            bot_username=result['bot_username'],
            chat_id=chat_id,
            chat_name=result['chat_name'],
            chat_type=result['chat_type'],
            is_private=is_private
        )
        
        db.session.add(bot)
        db.session.commit()
        
        return jsonify({
            'message': 'Telegram bot added successfully',
            'bot': bot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create bot', 'details': str(e)}), 500

@telegram_bots_bp.route('/telegram-bots/<bot_id>', methods=['GET'])
@jwt_required()
def get_telegram_bot(bot_id):
    try:
        current_user_id = get_jwt_identity()
        
        bot = TelegramBot.query.filter_by(
            id=bot_id,
            user_id=current_user_id
        ).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        return jsonify({
            'bot': bot.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get bot', 'details': str(e)}), 500

@telegram_bots_bp.route('/telegram-bots/<bot_id>', methods=['PUT'])
@jwt_required()
def update_telegram_bot(bot_id):
    try:
        current_user_id = get_jwt_identity()
        
        bot = TelegramBot.query.filter_by(
            id=bot_id,
            user_id=current_user_id
        ).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        data = request.get_json()
        
        # Update bot token if provided
        if 'bot_token' in data:
            new_bot_token = data['bot_token'].strip()
            
            # Validate new bot token
            is_valid, result = validate_telegram_bot(new_bot_token, bot.chat_id)
            if not is_valid:
                return jsonify({'error': result}), 400
            
            bot.bot_token = new_bot_token
            bot.bot_username = result['bot_username']
        
        # Update other fields
        if 'chat_name' in data:
            bot.chat_name = data['chat_name'].strip()
        
        if 'is_private' in data:
            bot.is_private = data['is_private']
        
        if 'is_active' in data:
            bot.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bot updated successfully',
            'bot': bot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update bot', 'details': str(e)}), 500

@telegram_bots_bp.route('/telegram-bots/<bot_id>', methods=['DELETE'])
@jwt_required()
def delete_telegram_bot(bot_id):
    try:
        current_user_id = get_jwt_identity()
        
        bot = TelegramBot.query.filter_by(
            id=bot_id,
            user_id=current_user_id
        ).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Check if bot has active campaigns
        if bot.campaigns:
            active_campaigns = [c for c in bot.campaigns if c.is_active]
            if active_campaigns:
                return jsonify({
                    'error': 'Cannot delete bot with active campaigns. Please deactivate campaigns first.'
                }), 400
        
        db.session.delete(bot)
        db.session.commit()
        
        return jsonify({
            'message': 'Bot deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete bot', 'details': str(e)}), 500

@telegram_bots_bp.route('/telegram-bots/<bot_id>/test', methods=['POST'])
@jwt_required()
def test_telegram_bot(bot_id):
    try:
        current_user_id = get_jwt_identity()
        
        bot = TelegramBot.query.filter_by(
            id=bot_id,
            user_id=current_user_id
        ).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Test bot connection
        is_valid, result = validate_telegram_bot(bot.bot_token, bot.chat_id)
        
        if is_valid:
            return jsonify({
                'message': 'Bot connection successful',
                'bot_info': result
            }), 200
        else:
            return jsonify({
                'error': 'Bot connection failed',
                'details': result
            }), 400
        
    except Exception as e:
        return jsonify({'error': 'Failed to test bot', 'details': str(e)}), 500

