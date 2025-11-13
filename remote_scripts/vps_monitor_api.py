#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル名: vps_monitor_api.py
説明: VPS監視APIサーバー - Home Assistantと通信するためのRESTful API
作成日: 2025-11-13
最終更新: 2025-11-13

このスクリプトはVPS上で動作し、以下の機能を提供します：
- システムステータス監視（CPU、メモリ、ディスク）
- SSH/VPN攻撃ログの解析
- UFW防火墙によるIP封禁/解除
- 脅威レベルの評価
- 緊急ロックダウン機能
"""

import os
import sys
import re
import subprocess
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from flask import Flask, jsonify, request
from functools import wraps

# Windows環境対応（開発用）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ha_monitor_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask アプリケーション
app = Flask(__name__)

# 設定
API_TOKEN = os.environ.get('API_TOKEN', 'your-secure-token-here')
API_PORT = int(os.environ.get('API_PORT', 5001))
AUTH_LOG_PATH = '/var/log/auth.log'
WHITELIST_FILE = '/etc/ha_monitor/whitelist.conf'
EMERGENCY_MODE_FILE = '/tmp/ha_monitor_emergency.lock'

# 統計データのキャッシュ
_cache = {
    'last_update': None,
    'stats': None
}
CACHE_DURATION = 30  # 秒


# ==================== ユーティリティ関数 ====================

def run_command(command, shell=False):
    """
    シェルコマンドを実行して結果を返す

    Args:
        command: 実行するコマンド（リストまたは文字列）
        shell: シェル経由で実行するか

    Returns:
        tuple: (stdout, stderr, returncode)
    """
    try:
        if isinstance(command, str) and not shell:
            command = command.split()

        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        logger.error(f"コマンドがタイムアウトしました: {command}")
        return "", "Timeout", -1
    except Exception as e:
        logger.error(f"コマンド実行エラー: {e}")
        return "", str(e), -1


def get_system_stats():
    """
    システムステータスを取得

    Returns:
        dict: CPU、メモリ、運行時間などの情報
    """
    stats = {}

    # CPU使用率を取得
    try:
        # top -bn1 でCPU使用率を取得
        stdout, _, _ = run_command("top -bn1", shell=True)
        # %Cpu(s): の行から idle を抽出
        for line in stdout.split('\n'):
            if '%Cpu(s)' in line or 'Cpu(s)' in line:
                # 例: %Cpu(s):  2.3 us,  1.0 sy,  0.0 ni, 96.3 id, ...
                match = re.search(r'(\d+\.?\d*)\s*id', line)
                if match:
                    idle = float(match.group(1))
                    stats['cpu_usage'] = round(100.0 - idle, 1)
                    break

        if 'cpu_usage' not in stats:
            stats['cpu_usage'] = 0.0
    except Exception as e:
        logger.error(f"CPU使用率取得エラー: {e}")
        stats['cpu_usage'] = 0.0

    # メモリ使用率を取得
    try:
        stdout, _, _ = run_command(['free', '-m'])
        # Mem: 行を解析
        for line in stdout.split('\n'):
            if line.startswith('Mem:'):
                parts = line.split()
                total = float(parts[1])
                used = float(parts[2])
                stats['memory_usage'] = round((used / total) * 100, 1)
                stats['memory_total_mb'] = int(total)
                stats['memory_used_mb'] = int(used)
                break

        if 'memory_usage' not in stats:
            stats['memory_usage'] = 0.0
    except Exception as e:
        logger.error(f"メモリ使用率取得エラー: {e}")
        stats['memory_usage'] = 0.0

    # システム運行時間を取得
    try:
        stdout, _, _ = run_command(['uptime', '-p'])
        stats['uptime'] = stdout.strip().replace('up ', '')
    except Exception as e:
        logger.error(f"稼働時間取得エラー: {e}")
        stats['uptime'] = 'unknown'

    # ディスク使用率を取得
    try:
        stdout, _, _ = run_command(['df', '-h', '/'])
        lines = stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            stats['disk_usage'] = parts[4].replace('%', '')
            stats['disk_total'] = parts[1]
            stats['disk_used'] = parts[2]
    except Exception as e:
        logger.error(f"ディスク使用率取得エラー: {e}")
        stats['disk_usage'] = '0'

    return stats


def parse_auth_log():
    """
    /var/log/auth.log を解析して攻撃情報を抽出

    Returns:
        dict: 攻撃統計情報
    """
    if not os.path.exists(AUTH_LOG_PATH):
        logger.warning(f"auth.logが見つかりません: {AUTH_LOG_PATH}")
        return {
            'ssh_attacks_today': 0,
            'vpn_attacks_today': 0,
            'blocked_ips_today': 0,
            'attack_ips': []
        }

    today = datetime.now().date()
    ssh_failed_attempts = defaultdict(int)
    vpn_failed_attempts = defaultdict(int)
    attack_ips = []

    # 正規表現パターン
    # SSH失败: Failed password for invalid user admin from 192.168.1.1 port 12345
    ssh_pattern = re.compile(
        r'Failed password for (?:invalid user )?(\w+) from ([\d\.]+) port (\d+)'
    )

    # VPN攻撃: 例 - WireGuard handshake failed from 192.168.1.1
    vpn_pattern = re.compile(
        r'(wireguard|openvpn).*(failed|invalid|rejected).*([\d\.]+)',
        re.IGNORECASE
    )

    try:
        with open(AUTH_LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # 今日の日付のログのみ処理
                try:
                    # Ubuntu 24.04のauth.logはISO 8601形式: 2025-11-13T05:56:27.584544+00:00
                    # 旧形式もサポート: Nov 13 10:30:45
                    if 'T' in line[:30]:  # ISO 8601形式
                        date_str = line.split('T')[0]
                        log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    else:  # 旧形式
                        date_str = ' '.join(line.split()[:3])
                        log_date = datetime.strptime(
                            f"{datetime.now().year} {date_str}",
                            "%Y %b %d %H:%M:%S"
                        ).date()

                    if log_date != today:
                        continue
                except:
                    continue

                # SSH攻撃を検出
                ssh_match = ssh_pattern.search(line)
                if ssh_match:
                    ip = ssh_match.group(2)
                    ssh_failed_attempts[ip] += 1

                # VPN攻撃を検出
                vpn_match = vpn_pattern.search(line)
                if vpn_match:
                    ip = vpn_match.group(3)
                    vpn_failed_attempts[ip] += 1

        # 攻撃IP情報を整理
        all_ips = set(list(ssh_failed_attempts.keys()) + list(vpn_failed_attempts.keys()))
        for ip in all_ips:
            attack_ips.append({
                'ip_address': ip,
                'ssh_attempts': ssh_failed_attempts.get(ip, 0),
                'vpn_attempts': vpn_failed_attempts.get(ip, 0),
                'total_attempts': ssh_failed_attempts.get(ip, 0) + vpn_failed_attempts.get(ip, 0)
            })

        # 攻撃数でソート
        attack_ips.sort(key=lambda x: x['total_attempts'], reverse=True)

        return {
            'ssh_attacks_today': sum(ssh_failed_attempts.values()),
            'vpn_attacks_today': sum(vpn_failed_attempts.values()),
            'attack_ips': attack_ips[:50],  # 上位50件
            'unique_attackers': len(all_ips)
        }

    except Exception as e:
        logger.error(f"auth.log解析エラー: {e}")
        return {
            'ssh_attacks_today': 0,
            'vpn_attacks_today': 0,
            'attack_ips': [],
            'unique_attackers': 0
        }


def get_ufw_status():
    """
    UFW防火墙状態を取得

    Returns:
        dict: 防火墙規則情報
    """
    try:
        stdout, _, returncode = run_command(['sudo', 'ufw', 'status', 'numbered'])

        if returncode != 0:
            logger.error("UFW status取得失敗")
            return {
                'firewall_active': False,
                'rules_count': 0,
                'blocked_ips': []
            }

        rules = []
        blocked_ips = []

        for line in stdout.split('\n'):
            # [ 1] Deny from 192.168.1.1
            match = re.search(r'Deny from ([\d\.]+)', line)
            if match:
                ip = match.group(1)
                blocked_ips.append(ip)
                rules.append(line.strip())

        return {
            'firewall_active': 'Status: active' in stdout,
            'rules_count': len(rules),
            'blocked_ips': blocked_ips,
            'blocked_ips_today': len(blocked_ips)  # 簡略化：今日封禁された数として扱う
        }

    except Exception as e:
        logger.error(f"UFW状態取得エラー: {e}")
        return {
            'firewall_active': False,
            'rules_count': 0,
            'blocked_ips': [],
            'blocked_ips_today': 0
        }


def calculate_threat_level(attack_count):
    """
    攻撃回数から脅威レベルを計算

    Args:
        attack_count: 総攻撃回数

    Returns:
        str: 'low', 'medium', 'high', 'critical'
    """
    if attack_count < 10:
        return 'low'
    elif attack_count < 50:
        return 'medium'
    elif attack_count < 200:
        return 'high'
    else:
        return 'critical'


# ==================== API認証 ====================

def require_token(f):
    """APIトークン認証デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            logger.warning("認証ヘッダーなし")
            return jsonify({'error': 'Unauthorized'}), 401

        if not auth_header.startswith('Bearer '):
            logger.warning("無効な認証形式")
            return jsonify({'error': 'Invalid authorization format'}), 401

        token = auth_header.split(' ')[1]
        if token != API_TOKEN:
            logger.warning(f"無効なトークン: {token[:10]}...")
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function


# ==================== APIエンドポイント ====================

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック（認証不要）"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '0.2.0'
    })


@app.route('/api/status', methods=['GET'])
@require_token
def get_status():
    """システムステータスを取得"""
    try:
        logger.info("システムステータス要求")

        # システム統計を取得
        system_stats = get_system_stats()

        # UFW状態を取得
        ufw_status = get_ufw_status()

        # auth.log解析（キャッシュ使用）
        global _cache
        now = datetime.now()
        if (_cache['last_update'] is None or
            (now - _cache['last_update']).total_seconds() > CACHE_DURATION):
            _cache['stats'] = parse_auth_log()
            _cache['last_update'] = now

        auth_stats = _cache['stats']

        # レスポンスを構築
        status = {
            'timestamp': now.isoformat(),
            'system_status': 'online',
            'cpu_usage': system_stats.get('cpu_usage', 0.0),
            'memory_usage': system_stats.get('memory_usage', 0.0),
            'disk_usage': system_stats.get('disk_usage', '0'),
            'uptime': system_stats.get('uptime', 'unknown'),
            'firewall_rules_count': ufw_status['rules_count'],
            'blocked_ips_today': ufw_status['blocked_ips_today'],
            'ssh_attacks_today': auth_stats['ssh_attacks_today'],
            'vpn_attacks_today': auth_stats['vpn_attacks_today'],
        }

        logger.info(f"ステータス返信: {status['ssh_attacks_today']} SSH攻撃, {status['vpn_attacks_today']} VPN攻撃")
        return jsonify(status)

    except Exception as e:
        logger.error(f"ステータス取得エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/threats', methods=['GET'])
@require_token
def get_threats():
    """脅威IPリストを取得"""
    try:
        logger.info("脅威リスト要求")

        # auth.log解析（キャッシュ使用）
        global _cache
        now = datetime.now()
        if (_cache['last_update'] is None or
            (now - _cache['last_update']).total_seconds() > CACHE_DURATION):
            _cache['stats'] = parse_auth_log()
            _cache['last_update'] = now

        auth_stats = _cache['stats']

        # UFW状態を取得（どのIPがブロック済みか確認）
        ufw_status = get_ufw_status()
        blocked_set = set(ufw_status['blocked_ips'])

        # 脅威リストを構築
        threat_list = []
        for attack in auth_stats['attack_ips']:
            ip = attack['ip_address']
            total = attack['total_attempts']

            # 個別の脅威レベルを計算
            if total >= 100:
                level = 'critical'
            elif total >= 50:
                level = 'high'
            elif total >= 10:
                level = 'medium'
            else:
                level = 'low'

            threat_list.append({
                'ip_address': ip,
                'country': 'Unknown',  # TODO: GeoIP lookup
                'attack_count': total,
                'threat_level': level,
                'last_attack_time': datetime.now().isoformat(),
                'blocked': ip in blocked_set
            })

        # 全体の脅威レベル
        total_attacks = auth_stats['ssh_attacks_today'] + auth_stats['vpn_attacks_today']
        overall_threat_level = calculate_threat_level(total_attacks)

        # 国別統計（簡略化）
        top_countries = [
            {'country': 'Unknown', 'count': len(threat_list)}
        ]

        response = {
            'timestamp': now.isoformat(),
            'threat_level': overall_threat_level,
            'total_threats': len(threat_list),
            'total_attacks': total_attacks,
            'threat_list': threat_list,
            'top_attack_countries': top_countries,
            'attack_trend': []  # TODO: 24時間トレンドデータ
        }

        logger.info(f"脅威リスト返信: {len(threat_list)} IP, レベル={overall_threat_level}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"脅威リスト取得エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/block', methods=['POST'])
@require_token
def block_ip():
    """IPアドレスをブロック"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        duration = data.get('duration')  # 未使用（将来の拡張用）

        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400

        # IP形式検証
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address):
            return jsonify({'error': 'Invalid IP address format'}), 400

        logger.info(f"IPブロック要求: {ip_address}")

        # UFWでIPをブロック
        stdout, stderr, returncode = run_command(
            ['sudo', 'ufw', 'deny', 'from', ip_address]
        )

        if returncode != 0:
            logger.error(f"UFWブロック失敗: {stderr}")
            return jsonify({
                'success': False,
                'error': f'Failed to block IP: {stderr}'
            }), 500

        logger.info(f"IP {ip_address} をブロックしました")

        return jsonify({
            'success': True,
            'message': f'IP {ip_address} blocked successfully',
            'ip_address': ip_address,
            'blocked_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"IPブロックエラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/unblock', methods=['POST'])
@require_token
def unblock_ip():
    """IPアドレスのブロックを解除"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')

        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400

        logger.info(f"IPブロック解除要求: {ip_address}")

        # UFWでブロックを削除
        stdout, stderr, returncode = run_command(
            ['sudo', 'ufw', 'delete', 'deny', 'from', ip_address]
        )

        if returncode != 0:
            logger.error(f"UFWブロック解除失敗: {stderr}")
            return jsonify({
                'success': False,
                'error': f'Failed to unblock IP: {stderr}'
            }), 500

        logger.info(f"IP {ip_address} のブロックを解除しました")

        return jsonify({
            'success': True,
            'message': f'IP {ip_address} unblocked successfully',
            'ip_address': ip_address,
            'unblocked_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"IPブロック解除エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/whitelist', methods=['GET', 'POST', 'DELETE'])
@require_token
def manage_whitelist():
    """ホワイトリスト管理"""
    try:
        if request.method == 'GET':
            # ホワイトリスト取得
            if os.path.exists(WHITELIST_FILE):
                with open(WHITELIST_FILE, 'r') as f:
                    whitelist = [line.strip() for line in f if line.strip()]
            else:
                whitelist = []

            return jsonify({'whitelist': whitelist})

        elif request.method == 'POST':
            # ホワイトリストに追加
            data = request.get_json()
            ip_address = data.get('ip_address')

            if not ip_address:
                return jsonify({'error': 'IP address required'}), 400

            # ファイルに追加
            os.makedirs(os.path.dirname(WHITELIST_FILE), exist_ok=True)
            with open(WHITELIST_FILE, 'a') as f:
                f.write(f"{ip_address}\n")

            logger.info(f"ホワイトリストに追加: {ip_address}")
            return jsonify({'success': True, 'message': 'Added to whitelist'})

        elif request.method == 'DELETE':
            # ホワイトリストから削除
            data = request.get_json()
            ip_address = data.get('ip_address')

            if not ip_address:
                return jsonify({'error': 'IP address required'}), 400

            if os.path.exists(WHITELIST_FILE):
                with open(WHITELIST_FILE, 'r') as f:
                    lines = f.readlines()

                with open(WHITELIST_FILE, 'w') as f:
                    for line in lines:
                        if line.strip() != ip_address:
                            f.write(line)

            logger.info(f"ホワイトリストから削除: {ip_address}")
            return jsonify({'success': True, 'message': 'Removed from whitelist'})

    except Exception as e:
        logger.error(f"ホワイトリスト管理エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/ip_info', methods=['POST'])
@require_token
def get_ip_info():
    """IPアドレスの詳細情報を取得"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')

        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400

        # auth.log解析
        auth_stats = parse_auth_log()

        # 指定IPの情報を検索
        ip_info = None
        for attack in auth_stats['attack_ips']:
            if attack['ip_address'] == ip_address:
                ip_info = attack
                break

        if ip_info is None:
            return jsonify({
                'ip_address': ip_address,
                'found': False,
                'message': 'No attack records found for this IP'
            })

        # UFW状態を確認
        ufw_status = get_ufw_status()
        is_blocked = ip_address in ufw_status['blocked_ips']

        response = {
            'ip_address': ip_address,
            'found': True,
            'country': 'Unknown',  # TODO: GeoIP lookup
            'city': 'Unknown',
            'isp': 'Unknown',
            'threat_score': min(ip_info['total_attempts'] / 10, 10),  # 0-10スケール
            'total_attacks': ip_info['total_attempts'],
            'ssh_attempts': ip_info['ssh_attempts'],
            'vpn_attempts': ip_info['vpn_attempts'],
            'first_seen': datetime.now().isoformat(),  # TODO: 実際の初回検出時刻
            'last_seen': datetime.now().isoformat(),
            'blocked': is_blocked
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"IP情報取得エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/emergency', methods=['POST'])
@require_token
def emergency_lockdown():
    """緊急ロックダウン"""
    try:
        logger.warning("🚨 緊急ロックダウン実行")

        # ロックモードファイルを作成
        with open(EMERGENCY_MODE_FILE, 'w') as f:
            f.write(f"Emergency lockdown activated at {datetime.now().isoformat()}\n")

        # TODO: 実際のロックダウン処理
        # - すべての新規接続を拒否
        # - ホワイトリストIPのみ許可
        # - 管理者に通知

        actions = [
            "すべての新規接続をブロック",
            "ホワイトリストIPのみ許可",
            "管理者に通知送信",
            "ログ記録強化"
        ]

        return jsonify({
            'success': True,
            'message': 'Emergency lockdown activated',
            'timestamp': datetime.now().isoformat(),
            'actions': actions
        })

    except Exception as e:
        logger.error(f"緊急ロックダウンエラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== メイン ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 VPS監視APIサーバーを起動しています")
    logger.info("=" * 60)
    logger.info(f"📍 ポート: {API_PORT}")
    logger.info(f"🔑 認証: Bearer Token")
    logger.info(f"📝 ログ: /var/log/ha_monitor_api.log")
    logger.info("=" * 60)

    # 権限チェック
    if os.geteuid() == 0:
        logger.warning("⚠️  rootユーザーで実行されています")

    # ディレクトリ作成
    os.makedirs(os.path.dirname(WHITELIST_FILE), exist_ok=True)

    # サーバー起動
    app.run(host='0.0.0.0', port=API_PORT, debug=False)
