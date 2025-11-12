#!/bin/bash
# VPS監視APIの自動インストールスクリプト

set -e

echo "=========================================="
echo "HA IP Monitor - VPS監視APIインストーラー"
echo "=========================================="
echo ""

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# エラーハンドラ
error_exit() {
    echo -e "${RED}エラー: $1${NC}" >&2
    exit 1
}

# 成功メッセージ
success_msg() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 警告メッセージ
warning_msg() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Pythonバージョンチェック
echo "Pythonバージョンを確認中..."
if ! command -v python3 &> /dev/null; then
    error_exit "Python3がインストールされていません"
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
success_msg "Python $PYTHON_VERSION が検出されました"

# pipのインストール確認
echo "pipを確認中..."
if ! command -v pip3 &> /dev/null; then
    warning_msg "pipがインストールされていません。インストールします..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
success_msg "pipが利用可能です"

# インストールディレクトリの作成
INSTALL_DIR="/opt/ha_ip_monitor"
echo "インストールディレクトリを作成中: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
success_msg "ディレクトリを作成しました"

# スクリプトファイルのコピー
echo "監視スクリプトをコピー中..."
sudo cp vps_monitor_api.py "$INSTALL_DIR/"
sudo cp requirements.txt "$INSTALL_DIR/"
success_msg "スクリプトをコピーしました"

# 依存関係のインストール
echo "Python依存関係をインストール中..."
sudo pip3 install -r "$INSTALL_DIR/requirements.txt"
success_msg "依存関係をインストールしました"

# 環境変数の設定
echo ""
echo "API設定を行います..."
read -p "APIポート番号 [デフォルト: 5001]: " API_PORT
API_PORT=${API_PORT:-5001}

read -sp "APIトークン [ランダム生成する場合はEnter]: " API_TOKEN
echo ""
if [ -z "$API_TOKEN" ]; then
    API_TOKEN=$(openssl rand -hex 32)
    echo "ランダムなAPIトークンを生成しました: $API_TOKEN"
fi

# 環境変数ファイルの作成
ENV_FILE="$INSTALL_DIR/.env"
sudo bash -c "cat > $ENV_FILE" <<EOF
API_PORT=$API_PORT
API_TOKEN=$API_TOKEN
EOF
success_msg "環境変数ファイルを作成しました"

# systemdサービスファイルの作成
echo "systemdサービスを作成中..."
sudo bash -c "cat > /etc/systemd/system/ha-ip-monitor.service" <<EOF
[Unit]
Description=HA IP Monitor API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/python3 $INSTALL_DIR/vps_monitor_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
success_msg "systemdサービスファイルを作成しました"

# サービスの有効化と起動
echo "サービスを有効化して起動中..."
sudo systemctl daemon-reload
sudo systemctl enable ha-ip-monitor.service
sudo systemctl start ha-ip-monitor.service
success_msg "サービスを起動しました"

# ファイアウォール設定
echo ""
read -p "UFWファイアウォールルールを追加しますか? (y/n) [y]: " ADD_FIREWALL
ADD_FIREWALL=${ADD_FIREWALL:-y}

if [ "$ADD_FIREWALL" = "y" ] || [ "$ADD_FIREWALL" = "Y" ]; then
    echo "ファイアウォールルールを追加中..."
    if command -v ufw &> /dev/null; then
        sudo ufw allow "$API_PORT/tcp" comment 'HA IP Monitor API'
        success_msg "ファイアウォールルールを追加しました"
    else
        warning_msg "UFWがインストールされていません。手動でポートを開放してください。"
    fi
fi

# インストール完了
echo ""
echo "=========================================="
echo -e "${GREEN}インストールが完了しました!${NC}"
echo "=========================================="
echo ""
echo "サービスステータス:"
sudo systemctl status ha-ip-monitor.service --no-pager
echo ""
echo "重要な情報:"
echo "  - APIポート: $API_PORT"
echo "  - APIトークン: $API_TOKEN"
echo "  - ログ確認: sudo journalctl -u ha-ip-monitor.service -f"
echo "  - サービス再起動: sudo systemctl restart ha-ip-monitor.service"
echo ""
echo "この情報をHome Assistantの設定で使用してください。"
echo ""
