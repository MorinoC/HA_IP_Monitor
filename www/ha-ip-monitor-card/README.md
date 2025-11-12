# HA IP Monitor Custom Card

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
