#!/usr/bin/env python3
"""VPS監視APIサーバー - Home Assistantと通信するためのRESTful API"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from functools import wraps

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーションの初期化
app = Flask(__name__)

# 設定
API_TOKEN = os.environ.get('API_TOKEN', 'your-secure-token-here')
API_PORT = int(os.environ.get('API_PORT', 5001))


def require_token(f):
    """APIトークン認証デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f'Bearer {API_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/status', methods=['GET'])
@require_token
def get_status():
    """システムステータスを取得"""
    # TODO: 実際のシステムステータスを取得
    status = {
        'timestamp': datetime.now().isoformat(),
        'vps_status': 'online',
        'cpu_usage': 15.2,
        'memory_usage': 45.8,
        'ssh_status': 'running',
        'vpn_status': 'running',
        'vpn_connections': 4
    }
    return jsonify(status)


@app.route('/api/threats', methods=['GET'])
@require_token
def get_threats():
    """脅威IPリストを取得"""
    # TODO: 実際の脅威データを取得
    threats = {
        'timestamp': datetime.now().isoformat(),
        'blocked_ips_today': 47,
        'ssh_attacks_today': 156,
        'vpn_attacks_today': 38,
        'threat_level': 'medium',
        'threat_ips': [
            {
                'ip': '185.200.116.43',
                'attack_count': 23,
                'country': 'CN',
                'last_attack': '2 hours ago',
                'threat_level': 'high'
            }
        ]
    }
    return jsonify(threats)


@app.route('/api/block', methods=['POST'])
@require_token
def block_ip():
    """IPアドレスをブロック"""
    data = request.get_json()
    ip_address = data.get('ip_address')

    if not ip_address:
        return jsonify({'error': 'IP address required'}), 400

    # TODO: 実際のIPブロック処理を実装
    logger.info(f"IPをブロックします: {ip_address}")

    return jsonify({
        'success': True,
        'message': f'IP {ip_address} blocked successfully',
        'ip': ip_address,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/unblock', methods=['POST'])
@require_token
def unblock_ip():
    """IPアドレスのブロックを解除"""
    data = request.get_json()
    ip_address = data.get('ip_address')

    if not ip_address:
        return jsonify({'error': 'IP address required'}), 400

    # TODO: 実際のIPブロック解除処理を実装
    logger.info(f"IPのブロックを解除します: {ip_address}")

    return jsonify({
        'success': True,
        'message': f'IP {ip_address} unblocked successfully',
        'ip': ip_address,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/whitelist', methods=['GET', 'POST', 'DELETE'])
@require_token
def manage_whitelist():
    """ホワイトリストの管理"""
    if request.method == 'GET':
        # TODO: ホワイトリストを取得
        whitelist = ['192.168.0.190', '10.0.0.0/24']
        return jsonify({'whitelist': whitelist})

    elif request.method == 'POST':
        # TODO: ホワイトリストに追加
        data = request.get_json()
        ip_address = data.get('ip_address')
        logger.info(f"ホワイトリストに追加: {ip_address}")
        return jsonify({'success': True, 'message': 'Added to whitelist'})

    elif request.method == 'DELETE':
        # TODO: ホワイトリストから削除
        data = request.get_json()
        ip_address = data.get('ip_address')
        logger.info(f"ホワイトリストから削除: {ip_address}")
        return jsonify({'success': True, 'message': 'Removed from whitelist'})


@app.route('/api/ip_info', methods=['POST'])
@require_token
def get_ip_info():
    """IPアドレスの詳細情報を取得"""
    data = request.get_json()
    ip_address = data.get('ip_address')

    if not ip_address:
        return jsonify({'error': 'IP address required'}), 400

    # TODO: 実際のIP情報取得処理を実装
    ip_info = {
        'ip': ip_address,
        'country': 'China',
        'city': 'Beijing',
        'isp': 'Alibaba Cloud',
        'threat_level': 8.5,
        'attack_count': 156,
        'first_seen': '2 hours ago',
        'attack_types': ['SSH Brute Force']
    }
    return jsonify(ip_info)


@app.route('/api/emergency', methods=['POST'])
@require_token
def emergency_lockdown():
    """緊急ロックダウン"""
    # TODO: 緊急ロックダウン処理を実装
    logger.warning("緊急ロックダウンが実行されました")

    return jsonify({
        'success': True,
        'message': 'Emergency lockdown activated',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント（認証不要）"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    logger.info(f"VPS監視APIサーバーをポート {API_PORT} で起動します")
    app.run(host='0.0.0.0', port=API_PORT, debug=False)
