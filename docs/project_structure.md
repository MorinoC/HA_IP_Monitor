# HA IP Monitor - プロジェクト構造説明

## 📁 ディレクトリ構造

```
HA_IP_Monitor/
├── custom_components/          # Home Assistant カスタム統合
│   └── ha_ip_monitor/
│       ├── __init__.py         # 統合のエントリーポイント
│       ├── manifest.json       # 統合のメタデータ
│       ├── const.py           # 定数定義
│       ├── config_flow.py     # 設定フロー
│       └── translations/      # 多言語翻訳
│           ├── en.json        # 英語
│           └── zh-Hans.json   # 簡体字中国語
│
├── www/                       # フロントエンドリソース
│   └── ha-ip-monitor-card/
│       ├── ha-ip-monitor-card.js  # カスタムLovelaceカード
│       └── README.md          # カードの使用方法
│
├── remote_scripts/           # VPS デプロイメントスクリプト
│   ├── vps_monitor_api.py   # VPS 監視APIサーバー
│   ├── installer.sh         # 自動インストールスクリプト
│   ├── requirements.txt     # Python 依存関係
│   ├── config_template.yaml # 設定テンプレート
│   └── README.md           # VPS スクリプトの説明
│
├── docs/                    # ドキュメント
│   └── project_structure.md # このファイル
│
├── tests/                   # テスト（今後実装予定）
│
├── hacs.json               # HACS 統合設定
├── .gitignore             # Git 除外設定
├── LICENSE                # MIT ライセンス
└── README.md             # プロジェクト概要
```

## 📄 主要ファイルの説明

### Home Assistant 統合ファイル

#### `custom_components/ha_ip_monitor/__init__.py`
- 統合のメインエントリーポイント
- 統合のセットアップとアンロード処理
- プラットフォームの登録

#### `custom_components/ha_ip_monitor/manifest.json`
- HACS用のメタデータ
- 依存関係の定義
- バージョン情報

#### `custom_components/ha_ip_monitor/const.py`
- すべての定数定義
- センサー名、サービス名
- API エンドポイント
- デフォルト値

#### `custom_components/ha_ip_monitor/config_flow.py`
- ユーザー設定フロー
- VPS接続設定
- 認証方法の選択（パスワード/SSHキー）
- API設定

#### `custom_components/ha_ip_monitor/translations/`
- 多言語対応の翻訳ファイル
- 英語（en.json）
- 簡体字中国語（zh-Hans.json）

### VPS スクリプト

#### `remote_scripts/vps_monitor_api.py`
- Flask製のRESTful APIサーバー
- Home Assistantとの通信インターフェース
- エンドポイント:
  - `/api/status` - システムステータス
  - `/api/threats` - 脅威リスト
  - `/api/block` - IP封鎖
  - `/api/unblock` - IP封鎖解除
  - `/api/whitelist` - ホワイトリスト管理
  - `/api/ip_info` - IP詳細情報
  - `/api/emergency` - 緊急ロックダウン

#### `remote_scripts/installer.sh`
- VPSへの自動インストールスクリプト
- 依存関係のインストール
- systemdサービスの作成
- ファイアウォール設定

#### `remote_scripts/requirements.txt`
- Python依存パッケージリスト
- Flask, requests, paramiko等

#### `remote_scripts/config_template.yaml`
- VPS監視APIの設定テンプレート
- 監視設定、閾値、ホワイトリスト等

### フロントエンド

#### `www/ha-ip-monitor-card/ha-ip-monitor-card.js`
- カスタムLovelaceカード
- リアルタイム脅威表示
- 緊急ロックダウンボタン
- レスポンシブデザイン

### 設定ファイル

#### `hacs.json`
- HACS統合の設定
- 統合タイプ: integration
- サポートするドメイン: sensor

#### `.gitignore`
- Git管理から除外するファイル
- 認証情報、ログ、一時ファイル等

## 🔄 今後実装予定のファイル

### Phase 2 で追加予定

1. **`custom_components/ha_ip_monitor/coordinator.py`**
   - データ更新コーディネーター
   - VPS APIとの通信管理
   - データのキャッシング

2. **`custom_components/ha_ip_monitor/sensor.py`**
   - センサーエンティティの実装
   - 各種統計データの提供

3. **`custom_components/ha_ip_monitor/services.yaml`**
   - サービス定義
   - block_ip, unblock_ip 等

4. **`tests/`ディレクトリ**
   - ユニットテスト
   - 統合テスト

## 📊 ファイルサイズ統計

- Python ファイル: 4個
- JavaScript ファイル: 1個
- JSON ファイル: 3個
- YAML ファイル: 1個
- Markdown ファイル: 5個
- Shell スクリプト: 1個

## 🔐 セキュリティ関連ファイル

- `.gitignore`: 秘密情報の除外
- `LICENSE`: MITライセンス
- 認証情報は環境変数で管理

## 📝 開発ステータス

- ✅ **Phase 1完了**: 基礎フレームワーク
  - プロジェクト構造
  - 設定フロー
  - VPS APIフレームワーク
  - カスタムカード

- 🔄 **Phase 2進行中**: コア機能
  - データコーディネーター
  - センサー実装
  - サービス実装

- ⏳ **Phase 3計画中**: 拡張機能
  - 脅威情報統合
  - 高度な可視化
  - 通知システム
