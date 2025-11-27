from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from config.database import get_supabase_client
from config.settings import FLASK_HOST, FLASK_PORT, ADMIN_USER_IDS
from bot.services.user_service import UserService
from bot.services.broadcast_service import BroadcastService
from bot.services.priority_service import PrioritySlotService
from bot.services.payment_service import PaymentService
import hmac
import hashlib
import json
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app)

user_service = UserService()
broadcast_service = BroadcastService()
priority_service = PrioritySlotService()
payment_service = PaymentService()

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

# In-memory ad settings
ad_settings = {
    'ads_required': True  # Admin can toggle this
}

# Track users who watched ads (this session)
users_watched_ads_current_session = {}  # {user_id: True} for users who watched ads this session

# Track ad views statistics
ad_stats = {
    'views_completed': 0,  # Users who completed ad watching
    'views_uncompleted': 0  # Users who started but didn't complete
}

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
        data = request.json
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
        data = request.json
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
    """Get ad system settings"""
    return jsonify(ad_settings)

@app.route('/api/ads/settings', methods=['POST'])
def update_ads_settings():
    """Update ad system settings (admin only)"""
    try:
        data = request.json
        ads_required = data.get('ads_required')
        
        if ads_required is not None:
            ad_settings['ads_required'] = bool(ads_required)
            return jsonify({'message': 'Ad settings updated', 'settings': ad_settings})
        
        return jsonify({'error': 'Invalid request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/watched/<int:user_id>', methods=['POST'])
def mark_ad_watched(user_id):
    """Mark that user watched an ad and can send broadcast"""
    try:
        users_watched_ads_current_session[user_id] = True
        ad_stats['views_completed'] += 1  # Track completed view
        return jsonify({'message': 'Ad marked as watched', 'can_broadcast': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/started/<int:user_id>', methods=['POST'])
def mark_ad_started(user_id):
    """Track when user starts watching an ad"""
    try:
        ad_stats['views_uncompleted'] += 1  # Track started view
        return jsonify({'message': 'Ad view tracked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/check-watched/<int:user_id>', methods=['GET'])
def check_user_watched_ad(user_id):
    """Check if user watched an ad in current session"""
    try:
        watched = user_id in users_watched_ads_current_session
        return jsonify({'user_id': user_id, 'watched': watched})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/clear-watched/<int:user_id>', methods=['POST'])
def clear_user_watched_ad(user_id):
    """Clear ad watched status for user (for next broadcast)"""
    try:
        if user_id in users_watched_ads_current_session:
            del users_watched_ads_current_session[user_id]
        return jsonify({'message': 'Ad watched status cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/stats', methods=['GET'])
def get_ad_stats():
    """Get ad view statistics"""
    try:
        return jsonify({
            'views_completed': ad_stats['views_completed'],
            'views_uncompleted': ad_stats['views_uncompleted'],
            'total_views': ad_stats['views_completed'] + ad_stats['views_uncompleted'],
            'completion_rate': round((ad_stats['views_completed'] / max(1, ad_stats['views_uncompleted'] + ad_stats['views_completed'])) * 100, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/check/<int:user_id>', methods=['GET'])
def check_ad_watched(user_id):
    """Check if user watched ad and can broadcast"""
    try:
        watched = user_id in users_ads_watched
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
        data = request.json
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
        data = request.json
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

if __name__ == '__main__':
    print("🚀 Starting Flask Admin API...")
    print(f"📊 Dashboard will be available at http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
