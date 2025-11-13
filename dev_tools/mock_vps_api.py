#!/usr/bin/env python3
"""
ファイル名: mock_vps_api.py
説明: 開発用モックVPS APIサーバー
作成日: 2025-11-13
最終更新: 2025-11-13

使用方法:
    python dev_tools/mock_vps_api.py

説明:
    このスクリプトは、開発とテストのためにVPS APIをシミュレートします。
    実際のVPSに接続せずにHome Assistant統合をテストできます。
"""
import logging
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from functools import wraps

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# モック設定
API_TOKEN = "test-token-12345"
API_PORT = 5001

# モックデータ生成
def generate_mock_threats():
    """モック脅威データを生成"""
    countries = ["CN", "US", "RU", "KR", "DE", "FR", "GB"]
    threat_levels = ["low", "medium", "high", "critical"]

    threats = []
    for i in range(random.randint(5, 15)):
        threats.append({
            "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "country": random.choice(countries),
            "attack_count": random.randint(1, 200),
            "threat_level": random.choice(threat_levels),
            "last_attack_time": (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat() + "Z",
            "blocked": random.choice([True, False]),
        })

    return threats


def require_auth(f):
    """認証デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            logger.warning("認証ヘッダーがありません")
            return jsonify({"error": "認証が必要です"}), 401

        if not auth_header.startswith('Bearer '):
            logger.warning("無効な認証形式")
            return jsonify({"error": "無効な認証形式"}), 401

        token = auth_header.split(' ')[1]
        if token != API_TOKEN:
            logger.warning(f"無効なトークン: {token}")
            return jsonify({"error": "無効なトークン"}), 401

        return f(*args, **kwargs)

    return decorated_function


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック（認証不要）"""
    logger.info("ヘルスチェック要求")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.2.0-mock"
    })


@app.route('/api/status', methods=['GET'])
@require_auth
def get_status():
    """システムステータスを取得"""
    logger.info("ステータス要求")

    status_data = {
        "blocked_ips_today": random.randint(10, 50),
        "ssh_attacks_today": random.randint(100, 500),
        "vpn_attacks_today": random.randint(20, 100),
        "firewall_rules_count": random.randint(20, 35),
        "system_status": random.choice(["online", "online", "online", "warning"]),  # 主にonline
        "cpu_usage": round(random.uniform(10, 80), 1),
        "memory_usage": round(random.uniform(30, 70), 1),
        "uptime": f"{random.randint(1, 30)} days, {random.randint(0, 23)}:{random.randint(0, 59)}:{random.randint(0, 59)}",
    }

    return jsonify(status_data)


@app.route('/api/threats', methods=['GET'])
@require_auth
def get_threats():
    """脅威リストを取得"""
    logger.info("脅威データ要求")

    threat_list = generate_mock_threats()
    total_threats = len(threat_list)

    # 脅威レベルを計算
    if total_threats > 10:
        threat_level = "high"
    elif total_threats > 5:
        threat_level = "medium"
    else:
        threat_level = "low"

    # 国別集計
    country_counts = {}
    for threat in threat_list:
        country = threat["country"]
        country_counts[country] = country_counts.get(country, 0) + threat["attack_count"]

    top_countries = [
        {"country": country, "count": count}
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    threats_data = {
        "threat_level": threat_level,
        "total_threats": total_threats,
        "threat_list": threat_list,
        "top_attack_countries": top_countries,
        "attack_trend": [random.randint(5, 30) for _ in range(24)],  # 24時間のトレンド
    }

    return jsonify(threats_data)


@app.route('/api/block', methods=['POST'])
@require_auth
def block_ip():
    """IPをブロック"""
    data = request.get_json()
    ip_address = data.get('ip_address')
    duration = data.get('duration')

    if not ip_address:
        logger.warning("IP アドレスが指定されていません")
        return jsonify({"success": False, "error": "IPアドレスが必要です"}), 400

    logger.info(f"IP {ip_address} をブロック (期間: {duration})")

    return jsonify({
        "success": True,
        "message": f"IP {ip_address} をブロックしました",
        "ip_address": ip_address,
        "duration": duration,
        "blocked_at": datetime.now().isoformat()
    })


@app.route('/api/unblock', methods=['POST'])
@require_auth
def unblock_ip():
    """IPのブロックを解除"""
    data = request.get_json()
    ip_address = data.get('ip_address')

    if not ip_address:
        logger.warning("IPアドレスが指定されていません")
        return jsonify({"success": False, "error": "IPアドレスが必要です"}), 400

    logger.info(f"IP {ip_address} のブロックを解除")

    return jsonify({
        "success": True,
        "message": f"IP {ip_address} のブロックを解除しました",
        "ip_address": ip_address,
        "unblocked_at": datetime.now().isoformat()
    })


@app.route('/api/whitelist', methods=['GET', 'POST', 'DELETE'])
@require_auth
def manage_whitelist():
    """ホワイトリストを管理"""
    if request.method == 'GET':
        logger.info("ホワイトリスト取得")
        return jsonify({
            "whitelist": [
                "192.168.1.1",
                "10.0.0.1",
                "8.8.8.8"
            ]
        })

    elif request.method == 'POST':
        data = request.get_json()
        ip_address = data.get('ip_address')
        logger.info(f"ホワイトリストに {ip_address} を追加")
        return jsonify({
            "success": True,
            "message": f"{ip_address} をホワイトリストに追加しました"
        })

    elif request.method == 'DELETE':
        data = request.get_json()
        ip_address = data.get('ip_address')
        logger.info(f"ホワイトリストから {ip_address} を削除")
        return jsonify({
            "success": True,
            "message": f"{ip_address} をホワイトリストから削除しました"
        })


@app.route('/api/ip_info', methods=['POST'])
@require_auth
def get_ip_info():
    """IP詳細情報を取得"""
    data = request.get_json()
    ip_address = data.get('ip_address')

    logger.info(f"IP {ip_address} の情報を取得")

    return jsonify({
        "ip_address": ip_address,
        "country": random.choice(["CN", "US", "RU", "KR"]),
        "city": "Unknown",
        "isp": "Example ISP",
        "threat_score": random.randint(1, 100),
        "first_seen": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
        "last_seen": datetime.now().isoformat(),
        "total_attacks": random.randint(1, 500),
    })


@app.route('/api/emergency', methods=['POST'])
@require_auth
def emergency_lockdown():
    """緊急ロックダウン"""
    logger.warning("緊急ロックダウン実行")

    return jsonify({
        "success": True,
        "message": "緊急ロックダウンを実行しました",
        "locked_at": datetime.now().isoformat(),
        "actions": [
            "すべての新規接続をブロック",
            "既存の接続を監視",
            "管理者に通知"
        ]
    })


@app.errorhandler(404)
def not_found(error):
    """404 エラーハンドラー"""
    return jsonify({"error": "エンドポイントが見つかりません"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 エラーハンドラー"""
    return jsonify({"error": "内部サーバーエラー"}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 モック VPS API サーバーを起動しています...")
    print("=" * 60)
    print(f"📍 URL: http://localhost:{API_PORT}")
    print(f"🔑 API トークン: {API_TOKEN}")
    print("=" * 60)
    print("\n✅ 利用可能なエンドポイント:")
    print("  GET  /health                  - ヘルスチェック（認証不要）")
    print("  GET  /api/status              - システムステータス")
    print("  GET  /api/threats             - 脅威リスト")
    print("  POST /api/block               - IPブロック")
    print("  POST /api/unblock             - IPブロック解除")
    print("  *    /api/whitelist           - ホワイトリスト管理")
    print("  POST /api/ip_info             - IP詳細情報")
    print("  POST /api/emergency           - 緊急ロックダウン")
    print("\n💡 テスト例:")
    print(f'  curl http://localhost:{API_PORT}/health')
    print(f'  curl -H "Authorization: Bearer {API_TOKEN}" http://localhost:{API_PORT}/api/status')
    print("\n" + "=" * 60)
    print("🛑 Ctrl+C で停止\n")

    app.run(host='0.0.0.0', port=API_PORT, debug=True)
