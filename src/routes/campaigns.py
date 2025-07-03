from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User, TelegramBot, Campaign, TelegramLead, InviteLink
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os

campaigns_bp = Blueprint('campaigns', __name__)

def generate_script_code(campaign_id, base_url):
    """Generate JavaScript code for UTM tracking"""
    webhook_url = f"{base_url}/api/webhooks/utm-capture/{campaign_id}"
    
    script = f'''<script>
document.addEventListener("DOMContentLoaded", function() {{
  const btn = document.getElementById("btn-telegram");
  if (!btn) return;

  const base = "{webhook_url}";
  btn.href = base + window.location.search;
}});
</script>'''
    
    return script

@campaigns_bp.route('/campaigns', methods=['GET'])
@jwt_required()
def get_campaigns():
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters for filtering
        telegram_bot_id = request.args.get('telegram_bot_id')
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Build query
        query = Campaign.query.filter_by(user_id=current_user_id)
        
        if telegram_bot_id:
            query = query.filter_by(telegram_bot_id=telegram_bot_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Campaign.created_at))
        
        # Paginate
        campaigns = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get stats for each campaign
        campaign_data = []
        for campaign in campaigns.items:
            # Count total leads
            total_leads = TelegramLead.query.filter_by(campaign_id=campaign.id).count()
            
            # Count leads from last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_leads = TelegramLead.query.filter(
                TelegramLead.campaign_id == campaign.id,
                TelegramLead.created_at >= thirty_days_ago
            ).count()
            
            campaign_dict = campaign.to_dict()
            campaign_dict['stats'] = {
                'total_leads': total_leads,
                'recent_leads': recent_leads
            }
            campaign_data.append(campaign_dict)
        
        return jsonify({
            'campaigns': campaign_data,
            'pagination': {
                'page': campaigns.page,
                'pages': campaigns.pages,
                'per_page': campaigns.per_page,
                'total': campaigns.total,
                'has_next': campaigns.has_next,
                'has_prev': campaigns.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get campaigns', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns', methods=['POST'])
@jwt_required()
def create_campaign():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'telegram_bot_id')):
            return jsonify({'error': 'Name and telegram_bot_id are required'}), 400
        
        name = data['name'].strip()
        telegram_bot_id = data['telegram_bot_id']
        description = data.get('description', '').strip()
        
        # Validate telegram bot belongs to user
        bot = TelegramBot.query.filter_by(
            id=telegram_bot_id,
            user_id=current_user_id
        ).first()
        
        if not bot:
            return jsonify({'error': 'Telegram bot not found'}), 404
        
        if not bot.is_active:
            return jsonify({'error': 'Telegram bot is not active'}), 400
        
        # Create campaign
        campaign = Campaign(
            user_id=current_user_id,
            telegram_bot_id=telegram_bot_id,
            name=name,
            description=description
        )
        
        db.session.add(campaign)
        db.session.flush()  # Get the campaign ID
        
        # Generate webhook URLs
        base_url = request.host_url.rstrip('/')
        campaign.capture_webhook_url = f"{base_url}/api/webhooks/utm-capture/{campaign.id}"
        campaign.member_webhook_url = f"{base_url}/api/webhooks/telegram-member/{campaign.id}"
        
        # Generate script code
        campaign.script_code = generate_script_code(campaign.id, base_url)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign created successfully',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create campaign', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns/<campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        
        campaign = Campaign.query.filter_by(
            id=campaign_id,
            user_id=current_user_id
        ).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get detailed stats
        total_leads = TelegramLead.query.filter_by(campaign_id=campaign.id).count()
        
        # Leads by UTM source
        utm_source_stats = db.session.query(
            TelegramLead.utm_source,
            func.count(TelegramLead.id).label('count')
        ).filter_by(campaign_id=campaign.id).group_by(TelegramLead.utm_source).all()
        
        # Leads by UTM campaign
        utm_campaign_stats = db.session.query(
            TelegramLead.utm_campaign,
            func.count(TelegramLead.id).label('count')
        ).filter_by(campaign_id=campaign.id).group_by(TelegramLead.utm_campaign).all()
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_leads = TelegramLead.query.filter(
            TelegramLead.campaign_id == campaign.id,
            TelegramLead.created_at >= seven_days_ago
        ).order_by(desc(TelegramLead.created_at)).limit(10).all()
        
        campaign_dict = campaign.to_dict()
        campaign_dict['stats'] = {
            'total_leads': total_leads,
            'utm_source_breakdown': [{'source': s[0] or 'Unknown', 'count': s[1]} for s in utm_source_stats],
            'utm_campaign_breakdown': [{'campaign': c[0] or 'Unknown', 'count': c[1]} for c in utm_campaign_stats],
            'recent_leads': [lead.to_dict() for lead in recent_leads]
        }
        
        return jsonify({
            'campaign': campaign_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get campaign', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns/<campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        
        campaign = Campaign.query.filter_by(
            id=campaign_id,
            user_id=current_user_id
        ).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            campaign.name = data['name'].strip()
        
        if 'description' in data:
            campaign.description = data['description'].strip()
        
        if 'is_active' in data:
            campaign.is_active = data['is_active']
        
        # If telegram_bot_id is being changed, validate it
        if 'telegram_bot_id' in data:
            new_bot_id = data['telegram_bot_id']
            bot = TelegramBot.query.filter_by(
                id=new_bot_id,
                user_id=current_user_id
            ).first()
            
            if not bot:
                return jsonify({'error': 'Telegram bot not found'}), 404
            
            if not bot.is_active:
                return jsonify({'error': 'Telegram bot is not active'}), 400
            
            campaign.telegram_bot_id = new_bot_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign updated successfully',
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update campaign', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns/<campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        
        campaign = Campaign.query.filter_by(
            id=campaign_id,
            user_id=current_user_id
        ).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        db.session.delete(campaign)
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete campaign', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns/<campaign_id>/leads', methods=['GET'])
@jwt_required()
def get_campaign_leads(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Verify campaign belongs to user
        campaign = Campaign.query.filter_by(
            id=campaign_id,
            user_id=current_user_id
        ).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get query parameters for filtering
        utm_source = request.args.get('utm_source')
        utm_campaign = request.args.get('utm_campaign')
        utm_medium = request.args.get('utm_medium')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Build query
        query = TelegramLead.query.filter_by(campaign_id=campaign_id)
        
        if utm_source:
            query = query.filter_by(utm_source=utm_source)
        
        if utm_campaign:
            query = query.filter_by(utm_campaign=utm_campaign)
        
        if utm_medium:
            query = query.filter_by(utm_medium=utm_medium)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by creation date (newest first)
        query = query.order_by(desc(TelegramLead.created_at))
        
        # Paginate
        leads = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'leads': [lead.to_dict() for lead in leads.items],
            'pagination': {
                'page': leads.page,
                'pages': leads.pages,
                'per_page': leads.per_page,
                'total': leads.total,
                'has_next': leads.has_next,
                'has_prev': leads.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get leads', 'details': str(e)}), 500

@campaigns_bp.route('/campaigns/<campaign_id>/script', methods=['GET'])
@jwt_required()
def get_campaign_script(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        
        campaign = Campaign.query.filter_by(
            id=campaign_id,
            user_id=current_user_id
        ).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Regenerate script if needed
        if not campaign.script_code:
            base_url = request.host_url.rstrip('/')
            campaign.script_code = generate_script_code(campaign.id, base_url)
            db.session.commit()
        
        return jsonify({
            'script_code': campaign.script_code,
            'instructions': [
                '1. Copy the script code below',
                '2. Paste it in the <head> section of your webpage',
                '3. Make sure you have a button with id="btn-telegram" on your page',
                '4. The button will automatically redirect users to your Telegram channel with UTM tracking'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get script', 'details': str(e)}), 500

