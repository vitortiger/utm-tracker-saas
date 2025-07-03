from flask import Blueprint, request, jsonify, redirect
from src.models import db
from src.models.campaign import Campaign
from src.models.invite_link import InviteLink
from src.models.lead import TelegramLead
from src.models.telegram_bot import TelegramBot
from datetime import datetime
import requests
import time
import random
import string

webhooks_bp = Blueprint('webhooks', __name__)

def generate_unique_code():
    """Generate a unique code for invite links"""
    timestamp36 = str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{timestamp36}{random_chars}"

def create_telegram_invite_link(bot_token, chat_id, link_name, is_private=False):
    """Create a Telegram invite link with the specified name"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/createChatInviteLink"
        
        params = {
            'chat_id': chat_id,
            'name': link_name
        }
        
        # Add expiration for private channels (24 hours)
        if is_private:
            expire_date = int(time.time()) + (24 * 60 * 60)  # 24 hours from now
            params['expire_date'] = expire_date
        
        response = requests.post(url, json=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return True, data['result']['invite_link']
            else:
                return False, data.get('description', 'Unknown error')
        else:
            return False, f"HTTP {response.status_code}"
            
    except requests.RequestException as e:
        return False, f"Request failed: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

@webhooks_bp.route('/webhooks/utm-capture/<campaign_id>', methods=['GET'])
def utm_capture_webhook(campaign_id):
    """Webhook to capture UTMs and create Telegram invite link"""
    try:
        # Get campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign or not campaign.is_active:
            return jsonify({'error': 'Campaign not found or inactive'}), 404
        
        # Get UTM parameters from query string
        utm_params = {
            'utm_source': request.args.get('utm_source', ''),
            'utm_medium': request.args.get('utm_medium', ''),
            'utm_campaign': request.args.get('utm_campaign', ''),
            'utm_content': request.args.get('utm_content', ''),
            'utm_term': request.args.get('utm_term', '')
        }
        
        # Generate unique code
        code = generate_unique_code()
        
        # Save UTM data to database
        invite_link = InviteLink(
            campaign_id=campaign_id,
            code=code,
            **utm_params
        )
        
        db.session.add(invite_link)
        db.session.flush()  # Get the ID
        
        # Get bot information
        bot = campaign.telegram_bot
        if not bot or not bot.is_active:
            db.session.rollback()
            return jsonify({'error': 'Bot not found or inactive'}), 404
        
        # Create Telegram invite link
        success, result = create_telegram_invite_link(
            bot.bot_token,
            bot.chat_id,
            code,
            bot.is_private
        )
        
        if success:
            # Save the invite link URL
            invite_link.invite_link_url = result
            db.session.commit()
            
            # Redirect user to Telegram
            return redirect(result)
        else:
            db.session.rollback()
            return jsonify({'error': f'Failed to create invite link: {result}'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Webhook error: {str(e)}'}), 500

@webhooks_bp.route('/webhooks/telegram-member/<campaign_id>', methods=['POST'])
def telegram_member_webhook(campaign_id):
    """Webhook to process Telegram member events"""
    try:
        # Get campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign or not campaign.is_active:
            return jsonify({'error': 'Campaign not found or inactive'}), 404
        
        # Get webhook data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Check if this is a chat_member update
        if 'chat_member' not in data:
            return jsonify({'message': 'Not a chat_member update'}), 200
        
        chat_member = data['chat_member']
        new_chat_member = chat_member.get('new_chat_member', {})
        
        # Check if user joined (status = member)
        if new_chat_member.get('status') != 'member':
            return jsonify({'message': 'User did not join'}), 200
        
        # Extract user information
        user_info = new_chat_member.get('user', {})
        telegram_id = str(user_info.get('id', ''))
        username = user_info.get('username', '')
        first_name = user_info.get('first_name', '')
        last_name = user_info.get('last_name', '')
        
        if not telegram_id:
            return jsonify({'error': 'No telegram_id found'}), 400
        
        # Extract invite link information
        invite_link_info = chat_member.get('invite_link', {})
        link_name = invite_link_info.get('name', '')
        
        # Get chat information
        chat_info = data.get('chat', {})
        group_name = chat_info.get('title', '')
        
        # Check if lead already exists for this campaign
        existing_lead = TelegramLead.query.filter_by(
            campaign_id=campaign_id,
            telegram_id=telegram_id
        ).first()
        
        if existing_lead:
            # Update existing lead (re-entry)
            existing_lead.status = 'member'
            existing_lead.entry_date = datetime.utcnow()
            existing_lead.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'message': 'Existing lead updated',
                'lead_id': existing_lead.id
            }), 200
        
        # Find UTM data using link_name (code)
        utm_data = {}
        invite_link_record = None
        
        if link_name:
            invite_link_record = InviteLink.query.filter_by(
                campaign_id=campaign_id,
                code=link_name
            ).first()
            
            if invite_link_record:
                utm_data = {
                    'utm_source': invite_link_record.utm_source,
                    'utm_medium': invite_link_record.utm_medium,
                    'utm_campaign': invite_link_record.utm_campaign,
                    'utm_content': invite_link_record.utm_content,
                    'utm_term': invite_link_record.utm_term
                }
        
        # Create new lead
        lead = TelegramLead(
            campaign_id=campaign_id,
            invite_link_id=invite_link_record.id if invite_link_record else None,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            group_name=group_name,
            entry_date=datetime.utcnow(),
            status='member',
            **utm_data
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return jsonify({
            'message': 'Lead created successfully',
            'lead_id': lead.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Webhook error: {str(e)}'}), 500

@webhooks_bp.route('/webhooks/telegram-member/<campaign_id>/setup', methods=['POST'])
def setup_telegram_webhook(campaign_id):
    """Setup Telegram webhook for a campaign"""
    try:
        # Get campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get bot
        bot = campaign.telegram_bot
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Setup webhook URL
        webhook_url = campaign.member_webhook_url
        
        # Configure Telegram webhook
        telegram_url = f"https://api.telegram.org/bot{bot.bot_token}/setWebhook"
        
        webhook_data = {
            'url': webhook_url,
            'allowed_updates': ['chat_member']
        }
        
        response = requests.post(telegram_url, json=webhook_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                # Update bot webhook URL
                bot.webhook_url = webhook_url
                db.session.commit()
                
                return jsonify({
                    'message': 'Webhook configured successfully',
                    'webhook_url': webhook_url
                }), 200
            else:
                return jsonify({
                    'error': f"Telegram API error: {data.get('description', 'Unknown error')}"
                }), 400
        else:
            return jsonify({
                'error': f"HTTP {response.status_code}"
            }), 400
            
    except requests.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Setup error: {str(e)}'}), 500

@webhooks_bp.route('/webhooks/telegram-member/<campaign_id>/remove', methods=['POST'])
def remove_telegram_webhook(campaign_id):
    """Remove Telegram webhook for a campaign"""
    try:
        # Get campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get bot
        bot = campaign.telegram_bot
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Remove webhook
        telegram_url = f"https://api.telegram.org/bot{bot.bot_token}/deleteWebhook"
        
        response = requests.post(telegram_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                # Clear bot webhook URL
                bot.webhook_url = None
                db.session.commit()
                
                return jsonify({
                    'message': 'Webhook removed successfully'
                }), 200
            else:
                return jsonify({
                    'error': f"Telegram API error: {data.get('description', 'Unknown error')}"
                }), 400
        else:
            return jsonify({
                'error': f"HTTP {response.status_code}"
            }), 400
            
    except requests.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Remove error: {str(e)}'}), 500

