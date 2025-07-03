from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User, Campaign, TelegramLead, TelegramBot
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    try:
        current_user_id = get_jwt_identity()
        
        # Get basic counts
        total_campaigns = Campaign.query.filter_by(user_id=current_user_id).count()
        active_campaigns = Campaign.query.filter_by(user_id=current_user_id, is_active=True).count()
        total_bots = TelegramBot.query.filter_by(user_id=current_user_id).count()
        
        # Get total leads across all campaigns
        total_leads = db.session.query(func.count(TelegramLead.id)).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(Campaign.user_id == current_user_id).scalar()
        
        # Get leads from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_leads = db.session.query(func.count(TelegramLead.id)).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            and_(
                Campaign.user_id == current_user_id,
                TelegramLead.created_at >= thirty_days_ago
            )
        ).scalar()
        
        # Get leads from last 7 days for trend
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        weekly_leads = db.session.query(func.count(TelegramLead.id)).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            and_(
                Campaign.user_id == current_user_id,
                TelegramLead.created_at >= seven_days_ago
            )
        ).scalar()
        
        # Get top performing campaigns (by lead count)
        top_campaigns = db.session.query(
            Campaign.id,
            Campaign.name,
            func.count(TelegramLead.id).label('lead_count')
        ).outerjoin(
            TelegramLead, Campaign.id == TelegramLead.campaign_id
        ).filter(
            Campaign.user_id == current_user_id
        ).group_by(
            Campaign.id, Campaign.name
        ).order_by(
            desc('lead_count')
        ).limit(5).all()
        
        # Get recent activity (last 10 leads)
        recent_activity = db.session.query(TelegramLead).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            Campaign.user_id == current_user_id
        ).order_by(
            desc(TelegramLead.created_at)
        ).limit(10).all()
        
        # Get UTM source breakdown
        utm_sources = db.session.query(
            TelegramLead.utm_source,
            func.count(TelegramLead.id).label('count')
        ).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            Campaign.user_id == current_user_id
        ).group_by(
            TelegramLead.utm_source
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        return jsonify({
            'overview': {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'total_bots': total_bots,
                'total_leads': total_leads or 0,
                'recent_leads': recent_leads or 0,
                'weekly_leads': weekly_leads or 0
            },
            'top_campaigns': [
                {
                    'id': campaign[0],
                    'name': campaign[1],
                    'lead_count': campaign[2]
                }
                for campaign in top_campaigns
            ],
            'recent_activity': [
                {
                    'id': lead.id,
                    'first_name': lead.first_name,
                    'username': lead.username,
                    'utm_source': lead.utm_source,
                    'utm_campaign': lead.utm_campaign,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None,
                    'campaign_name': lead.campaign.name if lead.campaign else None
                }
                for lead in recent_activity
            ],
            'utm_sources': [
                {
                    'source': source[0] or 'Unknown',
                    'count': source[1]
                }
                for source in utm_sources
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard overview', 'details': str(e)}), 500

@dashboard_bp.route('/dashboard/analytics', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        days = int(request.args.get('days', 30))  # Default to 30 days
        campaign_id = request.args.get('campaign_id')  # Optional filter by campaign
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build base query
        base_query = db.session.query(TelegramLead).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            and_(
                Campaign.user_id == current_user_id,
                TelegramLead.created_at >= start_date,
                TelegramLead.created_at <= end_date
            )
        )
        
        # Apply campaign filter if specified
        if campaign_id:
            base_query = base_query.filter(Campaign.id == campaign_id)
        
        # Get daily lead counts for timeline
        daily_leads = db.session.query(
            func.date(TelegramLead.created_at).label('date'),
            func.count(TelegramLead.id).label('count')
        ).join(
            Campaign, TelegramLead.campaign_id == Campaign.id
        ).filter(
            and_(
                Campaign.user_id == current_user_id,
                TelegramLead.created_at >= start_date,
                TelegramLead.created_at <= end_date
            )
        )
        
        if campaign_id:
            daily_leads = daily_leads.filter(Campaign.id == campaign_id)
        
        daily_leads = daily_leads.group_by(
            func.date(TelegramLead.created_at)
        ).order_by('date').all()
        
        # Get UTM breakdown
        utm_source_breakdown = base_query.with_entities(
            TelegramLead.utm_source,
            func.count(TelegramLead.id).label('count')
        ).group_by(TelegramLead.utm_source).order_by(desc('count')).all()
        
        utm_medium_breakdown = base_query.with_entities(
            TelegramLead.utm_medium,
            func.count(TelegramLead.id).label('count')
        ).group_by(TelegramLead.utm_medium).order_by(desc('count')).all()
        
        utm_campaign_breakdown = base_query.with_entities(
            TelegramLead.utm_campaign,
            func.count(TelegramLead.id).label('count')
        ).group_by(TelegramLead.utm_campaign).order_by(desc('count')).all()
        
        # Get campaign performance (if not filtering by specific campaign)
        campaign_performance = []
        if not campaign_id:
            campaign_performance = db.session.query(
                Campaign.id,
                Campaign.name,
                func.count(TelegramLead.id).label('lead_count')
            ).outerjoin(
                TelegramLead, and_(
                    Campaign.id == TelegramLead.campaign_id,
                    TelegramLead.created_at >= start_date,
                    TelegramLead.created_at <= end_date
                )
            ).filter(
                Campaign.user_id == current_user_id
            ).group_by(
                Campaign.id, Campaign.name
            ).order_by(
                desc('lead_count')
            ).all()
        
        return jsonify({
            'timeline': [
                {
                    'date': lead[0].isoformat() if lead[0] else None,
                    'count': lead[1]
                }
                for lead in daily_leads
            ],
            'utm_breakdown': {
                'sources': [
                    {'name': item[0] or 'Unknown', 'count': item[1]}
                    for item in utm_source_breakdown
                ],
                'mediums': [
                    {'name': item[0] or 'Unknown', 'count': item[1]}
                    for item in utm_medium_breakdown
                ],
                'campaigns': [
                    {'name': item[0] or 'Unknown', 'count': item[1]}
                    for item in utm_campaign_breakdown
                ]
            },
            'campaign_performance': [
                {
                    'id': campaign[0],
                    'name': campaign[1],
                    'lead_count': campaign[2]
                }
                for campaign in campaign_performance
            ],
            'filters': {
                'days': days,
                'campaign_id': campaign_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get analytics', 'details': str(e)}), 500

@dashboard_bp.route('/dashboard/export', methods=['POST'])
@jwt_required()
def export_dashboard_data():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get export parameters
        export_type = data.get('type', 'leads')  # leads, campaigns, analytics
        campaign_id = data.get('campaign_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Parse dates if provided
        date_filter = {}
        if start_date:
            date_filter['start'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            date_filter['end'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if export_type == 'leads':
            # Export leads data
            query = db.session.query(TelegramLead).join(
                Campaign, TelegramLead.campaign_id == Campaign.id
            ).filter(Campaign.user_id == current_user_id)
            
            if campaign_id:
                query = query.filter(Campaign.id == campaign_id)
            
            if date_filter.get('start'):
                query = query.filter(TelegramLead.created_at >= date_filter['start'])
            
            if date_filter.get('end'):
                query = query.filter(TelegramLead.created_at <= date_filter['end'])
            
            leads = query.order_by(desc(TelegramLead.created_at)).all()
            
            export_data = []
            for lead in leads:
                export_data.append({
                    'telegram_id': lead.telegram_id,
                    'username': lead.username,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'group_name': lead.group_name,
                    'utm_source': lead.utm_source,
                    'utm_medium': lead.utm_medium,
                    'utm_campaign': lead.utm_campaign,
                    'utm_content': lead.utm_content,
                    'utm_term': lead.utm_term,
                    'entry_date': lead.entry_date.isoformat() if lead.entry_date else None,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None,
                    'campaign_name': lead.campaign.name if lead.campaign else None
                })
            
            return jsonify({
                'data': export_data,
                'total_records': len(export_data),
                'export_type': 'leads'
            }), 200
            
        elif export_type == 'campaigns':
            # Export campaigns data
            campaigns = Campaign.query.filter_by(user_id=current_user_id).all()
            
            export_data = []
            for campaign in campaigns:
                # Get lead count for each campaign
                lead_count = TelegramLead.query.filter_by(campaign_id=campaign.id).count()
                
                campaign_data = campaign.to_dict()
                campaign_data['lead_count'] = lead_count
                export_data.append(campaign_data)
            
            return jsonify({
                'data': export_data,
                'total_records': len(export_data),
                'export_type': 'campaigns'
            }), 200
            
        else:
            return jsonify({'error': 'Invalid export type'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Failed to export data', 'details': str(e)}), 500

