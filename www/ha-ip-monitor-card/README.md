# HA IP Monitor Custom Card

> **Multi-language Documentation** | [中文](#中文文档) | [日本語](#日本語ドキュメント)

A custom Lovelace card for HA IP Monitor.

## Features

- Real-time threat statistics display
- Threat IP list visualization
- Emergency lockdown button
- Responsive design

## Installation

### Using HACS (Recommended)

When you install the HA IP Monitor integration from HACS, this card will be automatically available.

### Manual Installation

1. Create the `www` directory if it doesn't exist:
   ```bash
   mkdir -p /config/www/ha-ip-monitor-card
   ```

2. Copy the file:
   ```bash
   cp ha-ip-monitor-card.js /config/www/ha-ip-monitor-card/
   ```

3. Add to Lovelace resources:
   - Settings → Dashboard → Resources
   - URL: `/local/ha-ip-monitor-card/ha-ip-monitor-card.js`
   - Type: JavaScript Module

## Usage

### Add to Lovelace Dashboard

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
```

### Configuration Options

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
title: "Custom Title"     # Optional
show_threat_list: true    # Optional, default: true
```

## Display Content

- **Blocked IPs**: Number of IPs blocked today
- **SSH Attacks**: Number of SSH attack attempts
- **VPN Attacks**: Number of VPN attack attempts
- **Threat Level**: Current threat level
- **Threat List**: Real-time threat IP list
- **Action Buttons**: Emergency lockdown, refresh

## Troubleshooting

### Card Not Displaying

1. Clear browser cache (Ctrl + F5)
2. Verify the resource URL is correct
3. Check browser console for errors

### Data Not Updating

1. Verify the integration is configured correctly
2. Check if the VPS API server is running
3. Check Home Assistant logs

## For Developers

### Customization

You can edit `ha-ip-monitor-card.js` to customize the style and functionality.

### Debugging

Use the browser's developer tools (F12) console to view debug information.

---

# 中文文档

> **多语言文档** | [English](#ha-ip-monitor-custom-card) | [日本語](#日本語ドキュメント)

HA IP Monitor的自定义Lovelace卡片。

## 特性

- 实时威胁统计显示
- 威胁IP列表可视化
- 紧急锁定按钮
- 响应式设计

## 安装

### 使用HACS（推荐）

从HACS安装HA IP Monitor集成后，此卡片将自动可用。

### 手动安装

1. 如果不存在则创建`www`目录：
   ```bash
   mkdir -p /config/www/ha-ip-monitor-card
   ```

2. 复制文件：
   ```bash
   cp ha-ip-monitor-card.js /config/www/ha-ip-monitor-card/
   ```

3. 添加到Lovelace资源：
   - 设置 → 仪表板 → 资源
   - URL: `/local/ha-ip-monitor-card/ha-ip-monitor-card.js`
   - 类型: JavaScript Module

## 使用方法

### 添加到Lovelace仪表板

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
```

### 配置选项

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
title: "自定义标题"        # 可选
show_threat_list: true    # 可选，默认: true
```

## 显示内容

- **被阻止IP数**: 今日被阻止的IP数量
- **SSH攻击数**: SSH攻击尝试次数
- **VPN攻击数**: VPN攻击尝试次数
- **威胁等级**: 当前威胁级别
- **威胁列表**: 实时威胁IP列表
- **操作按钮**: 紧急锁定、刷新

## 故障排查

### 卡片未显示

1. 清除浏览器缓存（Ctrl + F5）
2. 验证资源URL是否正确
3. 检查浏览器控制台的错误

### 数据未更新

1. 验证集成是否正确配置
2. 检查VPS API服务器是否运行
3. 检查Home Assistant日志

## 开发者指南

### 自定义

可以编辑`ha-ip-monitor-card.js`来自定义样式和功能。

### 调试

使用浏览器的开发者工具（F12）控制台查看调试信息。

---

# 日本語ドキュメント

> **多言語ドキュメント** | [English](#ha-ip-monitor-custom-card) | [中文](#中文文档)

HA IP Monitor用のカスタムLovelaceカードです。

## 特徴

- リアルタイムの脅威統計表示
- 脅威IPリストの可視化
- 緊急ロックダウンボタン
- レスポンシブデザイン

## インストール方法

### HACSを使用する場合（推奨）

HA IP Monitor統合をHACSからインストールすると、このカードも自動的に利用可能になります。

### 手動インストール

1. `www`ディレクトリがない場合は作成:
   ```bash
   mkdir -p /config/www/ha-ip-monitor-card
   ```

2. ファイルをコピー:
   ```bash
   cp ha-ip-monitor-card.js /config/www/ha-ip-monitor-card/
   ```

3. Lovelaceリソースに追加:
   - 設定 → ダッシュボード → リソース
   - URL: `/local/ha-ip-monitor-card/ha-ip-monitor-card.js`
   - タイプ: JavaScript Module

## 使用方法

### Lovelaceダッシュボードに追加

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
```

### 設定オプション

```yaml
type: custom:ha-ip-monitor-card
entity: sensor.ha_ip_monitor_status
title: "カスタムタイトル"  # オプション
show_threat_list: true      # オプション、デフォルト: true
```

## 表示内容

- **被阻止IP数**: 今日ブロックされたIP数
- **SSH攻撃数**: SSH攻撃試行回数
- **VPN攻撃数**: VPN攻撃試行回数
- **威胁等级**: 現在の脅威レベル
- **脅威リスト**: リアルタイムの脅威IPリスト
- **アクションボタン**: 緊急ロックダウン、リフレッシュ

## トラブルシューティング

### カードが表示されない

1. ブラウザのキャッシュをクリア（Ctrl + F5）
2. リソースURLが正しいか確認
3. ブラウザのコンソールでエラーを確認

### データが更新されない

1. 統合が正しく設定されているか確認
2. VPS APIサーバーが起動しているか確認
3. Home Assistantのログを確認

## 開発者向け

### カスタマイズ

`ha-ip-monitor-card.js`を編集して、スタイルや機能をカスタマイズできます。

### デバッグ

ブラウザの開発者ツール（F12）のコンソールでデバッグ情報を確認できます。
