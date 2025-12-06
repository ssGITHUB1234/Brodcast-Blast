from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from config.database import get_supabase_client
from config.settings import FLASK_HOST, FLASK_PORT, ADMIN_USER_IDS, TELEGRAM_BOT_TOKEN
from bot.services.user_service import UserService
from bot.services.broadcast_service import BroadcastService
from bot.services.priority_service import PrioritySlotService
from bot.services.payment_service import PaymentService
from bot.services.slot_type_service import SlotTypeService
import hmac
import hashlib
import json
import os
import telebot
# Import bot to access registered handlers
try:
    from bot.main import bot as telegram_bot
except Exception as e:
    print(f"Warning: Could not import telegram_bot: {e}")
    telegram_bot = None

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app)

user_service = UserService()
broadcast_service = BroadcastService()
priority_service = PrioritySlotService()
payment_service = PaymentService()
slot_type_service = SlotTypeService()

# In-memory pricing cache
pricing_cache = {
    'time_1h': 5.0,
    'time_6h': 25.0,
    'time_12h': 45.0,
    'time_24h': 80.0,
    'count_5': 10.0,
    'count_10': 18.0,
    'count_25': 40.0,
    'count_50': 70.0,
}

# Import shared ads state (including shared settings)
from config.ads_state import (
    users_watched_ads as users_ads_watched, ad_stats, mark_ad_watched, mark_ad_started,
    user_watched_ad as check_user_watched_ad, clear_watched, get_stats as get_ad_stats_data,
    settings as ad_settings  # Use shared settings dict
)

# Monetag ad links management (direct links)
monetag_links = [
    {'id': 1, 'name': 'Default Link', 'link': 'https://linkmoneta.g.com/?link=10243712', 'active': True}
]
next_link_id = 2

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_USER_IDS

@app.route('/', methods=['GET'])
def admin_dashboard():
    """Serve admin dashboard"""
    return render_template('dashboard.html')

@app.route('/ad-viewer', methods=['GET'])
def ad_viewer():
    """Serve ad viewer page with timer"""
    return render_template('ad_viewer.html')

@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get all pricing"""
    return jsonify(pricing_cache)

@app.route('/api/pricing/<slot_key>', methods=['POST'])
def update_pricing(slot_key):
    """Update pricing for a slot"""
    try:
        data = request.json or {}
        price = float(data.get('price', 0))
        
        if slot_key not in pricing_cache:
            return jsonify({'error': 'Invalid slot key'}), 400
        
        if price < 0:
            return jsonify({'error': 'Price must be positive'}), 400
        
        pricing_cache[slot_key] = price
        return jsonify({'message': f'Price updated for {slot_key}', 'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Broadcast Bot API is running'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    try:
        db = get_supabase_client()
        
        users_response = db.table('users').select('*', count='exact').execute()
        broadcasts_response = db.table('broadcasts').select('*', count='exact').execute()
        priority_slots_response = db.table('priority_slots').select('*', count='exact').execute()
        
        active_users = db.table('users').select('*', count='exact').eq('active', True).eq('blocked', False).execute()
        sent_broadcasts = db.table('broadcasts').select('*', count='exact').eq('status', 'sent').execute()
        active_slots = db.table('priority_slots').select('*', count='exact').eq('active', True).execute()
        
        total_views = 0
        if broadcasts_response.data:
            for bc in broadcasts_response.data:
                total_views += bc.get('views', 0)
        
        total_revenue = 0
        completed_payments = db.table('payments').select('*').eq('status', 'completed').execute()
        if completed_payments.data:
            for payment in completed_payments.data:
                total_revenue += float(payment.get('amount', 0))
        
        return jsonify({
            'total_users': users_response.count or 0,
            'active_users': active_users.count or 0,
            'total_broadcasts': broadcasts_response.count or 0,
            'sent_broadcasts': sent_broadcasts.count or 0,
            'total_views': total_views,
            'total_priority_slots': priority_slots_response.count or 0,
            'active_priority_slots': active_slots.count or 0,
            'total_revenue': total_revenue
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        db = get_supabase_client()
        response = db.table('users').select('*').order('join_date', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    try:
        user = user_service.get_user(user_id)
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/block', methods=['POST'])
def block_user(user_id):
    """Block/unblock a user"""
    try:
        data = request.json or {}
        blocked = data.get('blocked', True)
        
        user = user_service.update_user(user_id, blocked=blocked)
        if user:
            return jsonify({'message': f"User {'blocked' if blocked else 'unblocked'} successfully", 'user': user})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/broadcasts', methods=['GET'])
def get_broadcasts():
    """Get all broadcasts"""
    try:
        db = get_supabase_client()
        status = request.args.get('status')
        
        query = db.table('broadcasts').select('*')
        if status:
            query = query.eq('status', status)
        
        response = query.order('created_at', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/broadcasts/<int:broadcast_id>', methods=['GET'])
def get_broadcast(broadcast_id):
    """Get specific broadcast"""
    try:
        broadcast = broadcast_service.get_broadcast(broadcast_id)
        if broadcast:
            return jsonify(broadcast)
        return jsonify({'error': 'Broadcast not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/broadcasts/<int:broadcast_id>', methods=['DELETE'])
def delete_broadcast_admin(broadcast_id):
    """Delete a broadcast"""
    try:
        db = get_supabase_client()
        db.table('broadcasts').delete().eq('broadcast_id', broadcast_id).execute()
        return jsonify({'message': 'Broadcast deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-analytics', methods=['GET'])
def get_user_analytics():
    """Get user broadcast analytics aggregated"""
    try:
        db = get_supabase_client()
        broadcasts = db.table('broadcasts').select('user_id, broadcast_id, views, sent_count').execute()
        
        user_stats = {}
        if broadcasts.data:
            for bc in broadcasts.data:
                uid = bc['user_id']
                if uid not in user_stats:
                    user_stats[uid] = {'user_id': uid, 'broadcast_count': 0, 'total_views': 0, 'total_sent': 0}
                user_stats[uid]['broadcast_count'] += 1
                user_stats[uid]['total_views'] += bc.get('views', 0)
                user_stats[uid]['total_sent'] += bc.get('sent_count', 0)
        
        return jsonify(list(user_stats.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/priority-slots', methods=['GET'])
def get_priority_slots():
    """Get all priority slots"""
    try:
        db = get_supabase_client()
        response = db.table('priority_slots').select('*').order('created_at', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/priority-slots/active', methods=['GET'])
def get_active_slot():
    """Get currently active priority slot"""
    try:
        active_slot = priority_service.get_active_priority_slot()
        if active_slot:
            return jsonify(active_slot)
        return jsonify({'message': 'No active priority slot'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/broadcasts', methods=['GET'])
def get_broadcast_analytics():
    """Get broadcast analytics"""
    try:
        db = get_supabase_client()
        response = db.table('analytics').select('*').order('timestamp', desc=True).limit(1000).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """Get all payments"""
    try:
        db = get_supabase_client()
        response = db.table('payments').select('*').order('timestamp', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/logs', methods=['GET'])
def get_admin_logs():
    """Get admin logs"""
    try:
        db = get_supabase_client()
        response = db.table('admin_logs').select('*').order('timestamp', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-paying', methods=['GET'])
def get_top_paying_users():
    """Get top paying users (by total payment amount)"""
    try:
        db = get_supabase_client()
        limit = request.args.get('limit', 10, type=int)
        
        # Get payments aggregated by user
        payments = db.table('payments').select('user_id, amount, status').execute()
        
        user_payments = {}
        if payments.data:
            for payment in payments.data:
                if payment.get('status') == 'completed':
                    uid = payment['user_id']
                    amount = float(payment.get('amount', 0))
                    if uid not in user_payments:
                        user_payments[uid] = 0
                    user_payments[uid] += amount
        
        # Sort by amount and get top users
        sorted_users = sorted(user_payments.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        result = []
        for user_id, total_amount in sorted_users:
            user = user_service.get_user(user_id)
            if user:
                result.append({
                    'user_id': user_id,
                    'first_name': user.get('first_name', 'N/A'),
                    'country': user.get('country', 'N/A'),
                    'total_paid': round(total_amount, 2),
                    'blocked': user.get('blocked', False)
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-broadcasting', methods=['GET'])
def get_top_broadcasting_users():
    """Get top broadcasting users (by broadcast count)"""
    try:
        db = get_supabase_client()
        limit = request.args.get('limit', 10, type=int)
        
        # Get broadcasts aggregated by user
        broadcasts = db.table('broadcasts').select('user_id, broadcast_id').execute()
        
        user_broadcasts = {}
        if broadcasts.data:
            for bc in broadcasts.data:
                uid = bc['user_id']
                if uid not in user_broadcasts:
                    user_broadcasts[uid] = 0
                user_broadcasts[uid] += 1
        
        # Sort by count and get top users
        sorted_users = sorted(user_broadcasts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        result = []
        for user_id, broadcast_count in sorted_users:
            user = user_service.get_user(user_id)
            if user:
                result.append({
                    'user_id': user_id,
                    'first_name': user.get('first_name', 'N/A'),
                    'country': user.get('country', 'N/A'),
                    'broadcast_count': broadcast_count,
                    'blocked': user.get('blocked', False)
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/settings', methods=['GET'])
def get_ads_settings():
    """Get ad system settings including points"""
    from config import ads_state
    return jsonify({
        'ads_required': ads_state.settings.get('ads_required', True),
        'points_per_ad': ads_state.settings.get('points_per_ad', 10),
        'points_required': ads_state.settings.get('points_required', 30)
    })

@app.route('/api/ads/settings', methods=['POST'])
def update_ads_settings():
    """Update ad system settings (admin only)"""
    try:
        from config import ads_state
        data = request.json
        updated = False
        
        if 'ads_required' in data:
            ads_state.settings['ads_required'] = bool(data['ads_required'])
            ad_settings['ads_required'] = bool(data['ads_required'])
            updated = True
        
        if 'points_per_ad' in data:
            points_per_ad = int(data['points_per_ad'])
            if points_per_ad > 0:
                ads_state.settings['points_per_ad'] = points_per_ad
                updated = True
        
        if 'points_required' in data:
            points_required = int(data['points_required'])
            if points_required >= 0:
                ads_state.settings['points_required'] = points_required
                updated = True
        
        if updated:
            return jsonify({
                'message': 'Settings updated',
                'settings': {
                    'ads_required': ads_state.settings.get('ads_required', True),
                    'points_per_ad': ads_state.settings.get('points_per_ad', 10),
                    'points_required': ads_state.settings.get('points_required', 30)
                }
            })
        
        return jsonify({'error': 'No valid settings provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/watched/<int:user_id>', methods=['POST'])
def mark_ad_watched_endpoint(user_id):
    """Mark that user watched an ad and can send broadcast"""
    try:
        # Mark in both user service and ads state
        user_service.mark_ad_watched(user_id)
        # Also update ads_state with timestamp for recency tracking
        mark_ad_watched(user_id)
        return jsonify({'message': 'Ad marked as watched', 'can_broadcast': True, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/started/<int:user_id>', methods=['POST'])
def mark_ad_started_endpoint(user_id):
    """Track when user starts watching an ad"""
    try:
        mark_ad_started(user_id)
        return jsonify({'message': 'Ad view tracked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/check-watched/<int:user_id>', methods=['GET'])
def check_ad_watched_endpoint(user_id):
    """Check if user watched an ad in current session"""
    try:
        watched = check_user_watched_ad(user_id)
        return jsonify({'user_id': user_id, 'watched': watched})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/clear-watched/<int:user_id>', methods=['POST'])
def clear_ad_watched_endpoint(user_id):
    """Clear ad watched status for user (for next broadcast)"""
    try:
        clear_watched(user_id)
        return jsonify({'message': 'Ad watched status cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/stats', methods=['GET'])
def get_ads_stats_endpoint():
    """Get ad view statistics"""
    try:
        stats = get_ad_stats_data()
        stats['completion_rate'] = round((stats['views_completed'] / max(1, stats['views_uncompleted'] + stats['views_completed'])) * 100, 1)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/complete/<int:user_id>', methods=['POST'])
def ad_complete_endpoint(user_id):
    """Ad completed - award points and notify user"""
    try:
        from config import ads_state
        
        # Mark ad as watched
        mark_ad_watched(user_id)
        
        # Award points for watching ad
        points_per_ad = ads_state.settings.get('points_per_ad', 10)
        points_required = ads_state.settings.get('points_required', 30)
        new_balance = user_service.add_points(user_id, points_per_ad)
        
        print(f"[AD_COMPLETE] Awarded {points_per_ad} points to user {user_id}. New balance: {new_balance}")
        
        # Send points notification to user
        if telegram_bot:
            try:
                if new_balance >= points_required:
                    # User has enough points now
                    telegram_bot.send_message(
                        user_id,
                        f"🎉 +{points_per_ad} points earned!\n\n"
                        f"💰 Your balance: {new_balance} points\n\n"
                        f"✅ You have enough points to send a broadcast!\n"
                        f"Use /create to send your broadcast now."
                    )
                else:
                    # User needs more points
                    points_needed = points_required - new_balance
                    ads_needed = -(-points_needed // points_per_ad)  # Ceiling division
                    telegram_bot.send_message(
                        user_id,
                        f"🎉 +{points_per_ad} points earned!\n\n"
                        f"💰 Your balance: {new_balance} points\n"
                        f"📊 Required for broadcast: {points_required} points\n\n"
                        f"⏳ Watch {ads_needed} more ad(s) to unlock broadcasting!"
                    )
                print(f"[AD_COMPLETE] Sent points notification to user {user_id}")
            except Exception as e:
                print(f"[AD_COMPLETE] Error sending message: {e}")
                import traceback
                traceback.print_exc()
        
        return jsonify({
            'message': 'Ad completed successfully', 
            'user_id': user_id,
            'points_awarded': points_per_ad,
            'new_balance': new_balance,
            'points_required': points_required,
            'can_broadcast': new_balance >= points_required
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/check/<int:user_id>', methods=['GET'])
def check_ad_watched(user_id):
    """Check if user watched ad and can broadcast"""
    try:
        watched = user_service.has_watched_ad_today(user_id)
        return jsonify({'user_id': user_id, 'watched_ad': watched, 'ads_required': ad_settings['ads_required']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/clear/<int:user_id>', methods=['POST'])
def clear_ad_watched(user_id):
    """Clear ad watched status (for next broadcast)"""
    try:
        users_ads_watched.discard(user_id)
        return jsonify({'message': 'Ad status cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/links', methods=['GET'])
def get_ad_links():
    """Get all Monetag ad links"""
    return jsonify(monetag_links)

@app.route('/api/ads/links', methods=['POST'])
def add_ad_link():
    """Add new Monetag ad link"""
    global next_link_id
    try:
        data = request.json or {}
        link = data.get('link', '').strip()
        name = data.get('name', 'New Link')
        
        if not link:
            return jsonify({'error': 'Link is required'}), 400
        
        # Check if link already exists
        if any(l['link'] == link for l in monetag_links):
            return jsonify({'error': 'Link already exists'}), 400
        
        new_link = {
            'id': next_link_id,
            'name': name,
            'link': link,
            'active': True
        }
        monetag_links.append(new_link)
        next_link_id += 1
        return jsonify({'message': 'Link added', 'link': new_link})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/links/<int:link_id>', methods=['PUT'])
def update_ad_link(link_id):
    """Update Monetag ad link name"""
    try:
        data = request.json or {}
        link = next((l for l in monetag_links if l['id'] == link_id), None)
        
        if not link:
            return jsonify({'error': 'Link not found'}), 404
        
        link['name'] = data.get('name', link['name'])
        link['active'] = data.get('active', link['active'])
        
        return jsonify({'message': 'Link updated', 'link': link})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/links/<int:link_id>', methods=['DELETE'])
def delete_ad_link(link_id):
    """Delete Monetag ad link"""
    global monetag_links
    try:
        monetag_links = [l for l in monetag_links if l['id'] != link_id]
        return jsonify({'message': 'Link deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/cryptopay', methods=['POST'])
def cryptopay_webhook():
    """Handle CryptoPay payment webhook"""
    try:
        from bot.services.payment_service import PaymentService
        from config.settings import CRYPTOPAY_API_KEY
        
        signature = request.headers.get('Crypto-Pay-Signature')
        body = request.data
        
        payment_service = PaymentService()
        if not payment_service.verify_cryptopay_webhook(body, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.get_json()
        if data.get('update_type') == 'invoice_paid':
            invoice = data.get('data', {})
            invoice_id = str(invoice.get('invoice_id'))
            
            payment_service.update_payment_status(invoice_id, 'completed')
            
            db = get_supabase_client()
            payment = db.table('payments').select('*').eq('transaction_id', invoice_id).execute()
            if payment.data:
                slot_id = payment.data[0]['slot_id']
                priority_service.activate_priority_slot(slot_id)
        
        return jsonify({'ok': True})
    except Exception as e:
        print(f"CryptoPay webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/xrocket', methods=['POST'])
def xrocket_webhook():
    """Handle xRocket payment webhook"""
    try:
        from bot.services.payment_service import PaymentService
        from config.settings import XROCKET_API_KEY
        
        signature = request.headers.get('Rocket-Pay-Signature')
        body = request.data
        
        payment_service = PaymentService()
        if not payment_service.verify_xrocket_webhook(body, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.get_json()
        if data.get('invoice_id'):
            invoice_id = str(data.get('invoice_id'))
            status = data.get('status')
            
            if status == 'paid':
                payment_service.update_payment_status(invoice_id, 'completed')
                
                db = get_supabase_client()
                payment = db.table('payments').select('*').eq('transaction_id', invoice_id).execute()
                if payment.data:
                    slot_id = payment.data[0]['slot_id']
                    priority_service.activate_priority_slot(slot_id)
        
        return jsonify({'ok': True})
    except Exception as e:
        print(f"xRocket webhook error: {e}")
        return jsonify({'error': str(e)}), 500

from bot.services.force_join_service import ForceJoinService
force_join_service = ForceJoinService()

@app.route('/api/force-join/channels', methods=['GET'])
def get_force_join_channels():
    """Get all force join channels"""
    try:
        channels = force_join_service.get_all_channels()
        return jsonify(channels)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/force-join/channels', methods=['POST'])
def add_force_join_channel():
    """Add a new force join channel"""
    try:
        data = request.json or {}
        channel_input = data.get('channel_id', '').strip()
        channel_name = data.get('channel_name', '').strip()
        
        if not channel_input:
            return jsonify({'error': 'Channel ID or username is required'}), 400
        
        # Always try to fetch channel info from Telegram to get the correct ID and username
        channel_info = force_join_service.get_channel_info(channel_input)
        if channel_info:
            # Use provided name or fallback to Telegram's title
            if not channel_name:
                channel_name = channel_info.get('title', channel_input)
            channel_username = channel_info.get('username')
            channel_id = str(channel_info.get('id'))
        else:
            return jsonify({'error': 'Could not fetch channel info. Make sure the bot is admin in the channel.'}), 400
        
        result = force_join_service.add_channel(channel_id, channel_name, channel_username)
        if result:
            return jsonify({'message': 'Channel added successfully', 'channel': result})
        return jsonify({'error': 'Failed to add channel'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/force-join/channels/<int:id>', methods=['PUT'])
def update_force_join_channel(id):
    """Update a force join channel"""
    try:
        data = request.json or {}
        updates = {}
        
        if 'channel_name' in data:
            updates['channel_name'] = data['channel_name']
        if 'active' in data:
            updates['active'] = data['active']
        if 'channel_username' in data:
            updates['channel_username'] = data['channel_username']
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        result = force_join_service.update_channel(id, **updates)
        if result:
            return jsonify({'message': 'Channel updated', 'channel': result})
        return jsonify({'error': 'Channel not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/force-join/channels/<int:id>', methods=['DELETE'])
def delete_force_join_channel(id):
    """Delete a force join channel"""
    try:
        if force_join_service.delete_channel(id):
            return jsonify({'message': 'Channel deleted'})
        return jsonify({'error': 'Failed to delete channel'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/force-join/check/<int:user_id>', methods=['GET'])
def check_force_join(user_id):
    """Check if user has joined all required channels"""
    try:
        joined_all, not_joined = force_join_service.check_all_channels(user_id)
        return jsonify({
            'joined_all': joined_all,
            'not_joined': not_joined
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types', methods=['GET'])
def get_slot_types():
    """Get all slot types"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        slot_types = slot_type_service.get_all_slot_types(active_only=active_only)
        return jsonify(slot_types)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types', methods=['POST'])
def create_slot_type():
    """Create a new slot type"""
    try:
        data = request.json or {}
        
        slot_key = data.get('slot_key')
        slot_category = data.get('slot_category')
        display_name = data.get('display_name')
        price = data.get('price', 0)
        
        if not slot_key or not slot_category or not display_name:
            return jsonify({'error': 'slot_key, slot_category, and display_name are required'}), 400
        
        if slot_category not in ('time', 'count'):
            return jsonify({'error': 'slot_category must be "time" or "count"'}), 400
        
        duration_hours = data.get('duration_hours')
        message_count = data.get('message_count')
        description = data.get('description')
        
        if slot_category == 'time' and not duration_hours:
            return jsonify({'error': 'duration_hours is required for time-based slots'}), 400
        
        if slot_category == 'count' and not message_count:
            return jsonify({'error': 'message_count is required for count-based slots'}), 400
        
        result = slot_type_service.create_slot_type(
            slot_key=slot_key,
            slot_category=slot_category,
            display_name=display_name,
            price=price,
            description=description,
            duration_hours=duration_hours,
            message_count=message_count
        )
        
        if result:
            return jsonify({'message': 'Slot type created', 'slot_type': result})
        return jsonify({'error': 'Failed to create slot type'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types/<int:id>', methods=['GET'])
def get_slot_type(id):
    """Get a single slot type"""
    try:
        slot_type = slot_type_service.get_slot_type(id)
        if slot_type:
            return jsonify(slot_type)
        return jsonify({'error': 'Slot type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types/<int:id>', methods=['PUT'])
def update_slot_type(id):
    """Update a slot type"""
    try:
        data = request.json or {}
        
        result = slot_type_service.update_slot_type(id, **data)
        if result:
            return jsonify({'message': 'Slot type updated', 'slot_type': result})
        return jsonify({'error': 'Slot type not found or no updates provided'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types/<int:id>', methods=['DELETE'])
def delete_slot_type(id):
    """Delete (deactivate) a slot type"""
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        
        if hard_delete:
            if slot_type_service.hard_delete_slot_type(id):
                return jsonify({'message': 'Slot type permanently deleted'})
        else:
            result = slot_type_service.delete_slot_type(id)
            if result:
                return jsonify({'message': 'Slot type deactivated', 'slot_type': result})
        
        return jsonify({'error': 'Failed to delete slot type'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slot-types/pricing', methods=['GET'])
def get_slot_types_pricing():
    """Get pricing dict for backward compatibility"""
    try:
        pricing = slot_type_service.get_pricing_dict()
        return jsonify(pricing)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram bot webhook updates (webhook mode for production)"""
    import traceback
    try:
        json_data = request.get_json()
        update_id = json_data.get('update_id', '?') if json_data else '?'
        
        print(f"\n[WEBHOOK] Received update {update_id}")
        print(f"[WEBHOOK] telegram_bot initialized: {telegram_bot is not None}")
        
        if not telegram_bot:
            print("❌ [WEBHOOK] Telegram bot NOT initialized - cannot process!")
            return jsonify({'ok': True})
        
        if not json_data:
            print(f"[WEBHOOK] No JSON data in update {update_id}")
            return jsonify({'ok': True})
        
        # Log what type of update this is
        if 'message' in json_data:
            print(f"[WEBHOOK] Message update from user {json_data['message'].get('from', {}).get('id', '?')}")
        elif 'callback_query' in json_data:
            callback_data = json_data['callback_query'].get('data', '?')
            user_id = json_data['callback_query'].get('from', {}).get('id', '?')
            print(f"[WEBHOOK] Callback query from user {user_id}: data={callback_data}")
        else:
            print(f"[WEBHOOK] Other update type: {list(json_data.keys())}")
        
        # Convert JSON to Update object and process through registered handlers
        try:
            print(f"[WEBHOOK] Converting JSON to Update object...")
            update = telebot.types.Update.de_json(json_data)
            if update:
                print(f"[WEBHOOK] Update object created, processing...")
                telegram_bot.process_new_updates([update])
                print(f"✓ [WEBHOOK] Processed update {update_id} successfully")
            else:
                print(f"❌ [WEBHOOK] Failed to create Update object from {update_id}")
        except Exception as e:
            print(f"❌ [WEBHOOK] Error processing update {update_id}: {e}")
            traceback.print_exc()
        
        return jsonify({'ok': True})
    except Exception as e:
        print(f"❌ [WEBHOOK] Telegram webhook error: {e}")
        traceback.print_exc()
        return jsonify({'ok': True})  # Always return 200 to Telegram

if __name__ == '__main__':
    print("🚀 Starting Flask Admin API...")
    print(f"📊 Dashboard will be available at http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
