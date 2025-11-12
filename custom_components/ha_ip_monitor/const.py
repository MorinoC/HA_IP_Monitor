"""HA IP Monitor用の定数定義"""

# ドメイン名
DOMAIN = "ha_ip_monitor"

# 設定キー
CONF_VPS_HOST = "vps_host"
CONF_VPS_PORT = "vps_port"
CONF_VPS_USERNAME = "vps_username"
CONF_VPS_PASSWORD = "vps_password"
CONF_VPS_SSH_KEY = "vps_ssh_key"
CONF_API_PORT = "api_port"
CONF_API_TOKEN = "api_token"
CONF_USE_SSH_KEY = "use_ssh_key"

# デフォルト値
DEFAULT_VPS_PORT = 22
DEFAULT_API_PORT = 5001
DEFAULT_SCAN_INTERVAL = 60  # 60秒ごとに更新

# センサー名
SENSOR_BLOCKED_IPS_TODAY = "blocked_ips_today"
SENSOR_SSH_ATTACKS_TODAY = "ssh_attacks_today"
SENSOR_VPN_ATTACKS_TODAY = "vpn_attacks_today"
SENSOR_VPS_SYSTEM_STATUS = "vps_system_status"
SENSOR_FIREWALL_RULES_COUNT = "firewall_rules_count"
SENSOR_CURRENT_THREAT_LEVEL = "current_threat_level"

# サービス名
SERVICE_BLOCK_IP = "block_ip"
SERVICE_UNBLOCK_IP = "unblock_ip"
SERVICE_ADD_TO_WHITELIST = "add_to_whitelist"
SERVICE_REMOVE_FROM_WHITELIST = "remove_from_whitelist"
SERVICE_GET_IP_INFO = "get_ip_info"
SERVICE_EMERGENCY_LOCKDOWN = "emergency_lockdown"

# 属性名
ATTR_IP_ADDRESS = "ip_address"
ATTR_ATTACK_COUNT = "attack_count"
ATTR_COUNTRY = "country"
ATTR_LAST_ATTACK_TIME = "last_attack_time"
ATTR_THREAT_LEVEL = "threat_level"
ATTR_ISP = "isp"
ATTR_BLOCK_DURATION = "block_duration"

# 脅威レベル
THREAT_LEVEL_LOW = "low"
THREAT_LEVEL_MEDIUM = "medium"
THREAT_LEVEL_HIGH = "high"
THREAT_LEVEL_CRITICAL = "critical"

# 更新間隔（秒）
UPDATE_INTERVAL = 60

# タイムアウト（秒）
TIMEOUT = 10

# API エンドポイント
API_ENDPOINT_STATUS = "/api/status"
API_ENDPOINT_THREATS = "/api/threats"
API_ENDPOINT_BLOCK_IP = "/api/block"
API_ENDPOINT_UNBLOCK_IP = "/api/unblock"
API_ENDPOINT_WHITELIST = "/api/whitelist"
API_ENDPOINT_IP_INFO = "/api/ip_info"
API_ENDPOINT_EMERGENCY = "/api/emergency"
