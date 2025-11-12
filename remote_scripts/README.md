# VPS Remote Scripts

このディレクトリには、VPSサーバーにデプロイするスクリプトが含まれています。

## ファイル一覧

- **vps_monitor_api.py** - VPS監視APIサーバー（Flask製）
- **installer.sh** - 自動インストールスクリプト
- **requirements.txt** - Python依存関係
- **config_template.yaml** - 設定ファイルのテンプレート

## インストール手順

### 1. VPSサーバーにファイルをアップロード

```bash
scp -r remote_scripts/* user@your-vps-ip:/tmp/ha_ip_monitor/
```

### 2. インストールスクリプトを実行

```bash
ssh user@your-vps-ip
cd /tmp/ha_ip_monitor
chmod +x installer.sh
sudo ./installer.sh
```

### 3. Home Assistantで設定

インストールスクリプトが完了すると、以下の情報が表示されます:
- APIポート
- APIトークン

これらの情報をHome Assistantの設定画面で入力してください。

## 手動インストール

### 依存関係のインストール

```bash
sudo pip3 install -r requirements.txt
```

### APIサーバーの起動

```bash
export API_PORT=5001
export API_TOKEN="your-secure-token"
python3 vps_monitor_api.py
```

## サービス管理

```bash
# サービスの状態確認
sudo systemctl status ha-ip-monitor.service

# サービスの起動
sudo systemctl start ha-ip-monitor.service

# サービスの停止
sudo systemctl stop ha-ip-monitor.service

# サービスの再起動
sudo systemctl restart ha-ip-monitor.service

# ログの確認
sudo journalctl -u ha-ip-monitor.service -f
```

## APIエンドポイント

- `GET /health` - ヘルスチェック（認証不要）
- `GET /api/status` - システムステータス取得
- `GET /api/threats` - 脅威リスト取得
- `POST /api/block` - IP封鎖
- `POST /api/unblock` - IP封鎖解除
- `GET/POST/DELETE /api/whitelist` - ホワイトリスト管理
- `POST /api/ip_info` - IP詳細情報取得
- `POST /api/emergency` - 緊急ロックダウン

## 認証

すべてのAPIエンドポイント（/health除く）は、Bearerトークン認証が必要です:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://your-vps-ip:5001/api/status
```

## トラブルシューティング

### サービスが起動しない

```bash
# ログを確認
sudo journalctl -u ha-ip-monitor.service -n 50

# 環境変数ファイルを確認
cat /opt/ha_ip_monitor/.env
```

### ポートが使用中

```bash
# ポート使用状況を確認
sudo netstat -tulpn | grep 5001

# 別のポートを使用
sudo systemctl stop ha-ip-monitor.service
# .envファイルのAPI_PORTを変更
sudo systemctl start ha-ip-monitor.service
```

## セキュリティ注意事項

1. **APIトークンは安全に保管してください**
2. **ファイアウォールで適切にポートを制限してください**
3. **可能であればWireGuard経由でのみアクセスを許可してください**
4. **定期的にログを確認してください**
