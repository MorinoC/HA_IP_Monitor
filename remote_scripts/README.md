# VPS Remote Scripts

> **Multi-language Documentation** | [中文](#中文文档) | [日本語](#日本語ドキュメント)

This directory contains scripts to be deployed on your VPS server.

## File List

- **vps_monitor_api.py** - VPS monitoring API server (Flask-based)
- **installer.sh** - Automatic installation script
- **requirements.txt** - Python dependencies
- **config_template.yaml** - Configuration file template

## Installation Steps

### 1. Upload Files to VPS Server

```bash
scp -r remote_scripts/* user@your-vps-ip:/tmp/ha_ip_monitor/
```

### 2. Run Installation Script

```bash
ssh user@your-vps-ip
cd /tmp/ha_ip_monitor
chmod +x installer.sh
sudo ./installer.sh
```

### 3. Configure in Home Assistant

After the installation script completes, the following information will be displayed:
- API Port
- API Token

Enter this information in the Home Assistant configuration screen.

## Manual Installation

### Install Dependencies

```bash
sudo pip3 install -r requirements.txt
```

### Start API Server

```bash
export API_PORT=5001
export API_TOKEN="your-secure-token"
python3 vps_monitor_api.py
```

## Service Management

```bash
# Check service status
sudo systemctl status ha-ip-monitor.service

# Start service
sudo systemctl start ha-ip-monitor.service

# Stop service
sudo systemctl stop ha-ip-monitor.service

# Restart service
sudo systemctl restart ha-ip-monitor.service

# View logs
sudo journalctl -u ha-ip-monitor.service -f
```

## API Endpoints

- `GET /health` - Health check (no authentication required)
- `GET /api/status` - Get system status
- `GET /api/threats` - Get threat list
- `POST /api/block` - Block IP address
- `POST /api/unblock` - Unblock IP address
- `GET/POST/DELETE /api/whitelist` - Whitelist management
- `POST /api/ip_info` - Get IP detailed information
- `POST /api/emergency` - Emergency lockdown

## Authentication

All API endpoints (except /health) require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://your-vps-ip:5001/api/status
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u ha-ip-monitor.service -n 50

# Check environment variables file
cat /opt/ha_ip_monitor/.env
```

### Port Already in Use

```bash
# Check port usage
sudo netstat -tulpn | grep 5001

# Use a different port
sudo systemctl stop ha-ip-monitor.service
# Change API_PORT in .env file
sudo systemctl start ha-ip-monitor.service
```

## Security Notes

1. **Keep your API token secure**
2. **Properly restrict ports with firewall**
3. **If possible, allow access only via WireGuard**
4. **Regularly check logs**

---

# 中文文档

> **多语言文档** | [English](#vps-remote-scripts) | [日本語](#日本語ドキュメント)

此目录包含要部署到VPS服务器的脚本。

## 文件列表

- **vps_monitor_api.py** - VPS监控API服务器（基于Flask）
- **installer.sh** - 自动安装脚本
- **requirements.txt** - Python依赖
- **config_template.yaml** - 配置文件模板

## 安装步骤

### 1. 上传文件到VPS服务器

```bash
scp -r remote_scripts/* user@your-vps-ip:/tmp/ha_ip_monitor/
```

### 2. 运行安装脚本

```bash
ssh user@your-vps-ip
cd /tmp/ha_ip_monitor
chmod +x installer.sh
sudo ./installer.sh
```

### 3. 在Home Assistant中配置

安装脚本完成后，将显示以下信息：
- API端口
- API令牌

在Home Assistant配置界面中输入这些信息。

## 手动安装

### 安装依赖

```bash
sudo pip3 install -r requirements.txt
```

### 启动API服务器

```bash
export API_PORT=5001
export API_TOKEN="your-secure-token"
python3 vps_monitor_api.py
```

## 服务管理

```bash
# 检查服务状态
sudo systemctl status ha-ip-monitor.service

# 启动服务
sudo systemctl start ha-ip-monitor.service

# 停止服务
sudo systemctl stop ha-ip-monitor.service

# 重启服务
sudo systemctl restart ha-ip-monitor.service

# 查看日志
sudo journalctl -u ha-ip-monitor.service -f
```

## API端点

- `GET /health` - 健康检查（无需认证）
- `GET /api/status` - 获取系统状态
- `GET /api/threats` - 获取威胁列表
- `POST /api/block` - 封锁IP地址
- `POST /api/unblock` - 解封IP地址
- `GET/POST/DELETE /api/whitelist` - 白名单管理
- `POST /api/ip_info` - 获取IP详细信息
- `POST /api/emergency` - 紧急锁定

## 认证

所有API端点（除了/health）都需要Bearer令牌认证：

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://your-vps-ip:5001/api/status
```

## 故障排查

### 服务无法启动

```bash
# 查看日志
sudo journalctl -u ha-ip-monitor.service -n 50

# 检查环境变量文件
cat /opt/ha_ip_monitor/.env
```

### 端口已被占用

```bash
# 检查端口使用情况
sudo netstat -tulpn | grep 5001

# 使用其他端口
sudo systemctl stop ha-ip-monitor.service
# 修改.env文件中的API_PORT
sudo systemctl start ha-ip-monitor.service
```

## 安全注意事项

1. **请妥善保管API令牌**
2. **使用防火墙适当限制端口**
3. **如果可能，仅允许通过WireGuard访问**
4. **定期检查日志**

---

# 日本語ドキュメント

> **多言語ドキュメント** | [English](#vps-remote-scripts) | [中文](#中文文档)

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
