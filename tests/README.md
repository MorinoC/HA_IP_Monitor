# HA IP Monitor - 测试指南

> **Multi-language Documentation** | [中文](#中文指南) | [日本語](#日本語ガイド)

This guide explains how to run tests for the HA IP Monitor integration.

## Prerequisites

### Required Software
- Python 3.9 or higher
- pip (Python package manager)

### Install Test Dependencies

```bash
# Navigate to project directory
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor

# Install test dependencies
pip install -r tests/requirements.txt
```

## Running Tests

### Run All Tests

```bash
# Run all unit tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=custom_components.ha_ip_monitor --cov-report=html
```

### Run Specific Test Files

```bash
# Test coordinator only
pytest tests/test_coordinator.py

# Test sensors only
pytest tests/test_sensor.py

# Test config flow only
pytest tests/test_config_flow.py
```

### Run Specific Test Functions

```bash
# Run a specific test function
pytest tests/test_coordinator.py::test_coordinator_initialization

# Run tests matching a pattern
pytest -k "test_sensor"
```

## Using Mock API Server

The project includes a mock VPS API server for development and testing.

### Start Mock Server

```bash
# Start the mock API server
python dev_tools/mock_vps_api.py
```

The server will start on `http://localhost:5001` with:
- **API Token**: `test-token-12345`
- **Mock data**: Random threat data is generated

### Test API Endpoints

```bash
# Health check (no authentication required)
curl http://localhost:5001/health

# Get system status
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/status

# Get threats
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/threats
```

### Use Mock Server with Home Assistant

1. Start the mock API server
2. Configure HA IP Monitor integration with:
   - VPS Host: `localhost` or `127.0.0.1`
   - API Port: `5001`
   - API Token: `test-token-12345`
3. The integration will connect to the mock server instead of a real VPS

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_coordinator.py      # Coordinator tests (15 tests)
├── test_sensor.py           # Sensor entity tests (14 tests)
├── test_config_flow.py      # Config flow tests (7 tests)
└── requirements.txt         # Test dependencies
```

## Test Coverage

Current test coverage:
- **Coordinator**: 15 unit tests
- **Sensors**: 14 unit tests
- **Config Flow**: 7 unit tests
- **Total**: 36 unit tests

## Troubleshooting

### Import Errors

If you see import errors, make sure you're in the project root directory:

```bash
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor
```

### Dependency Issues

Reinstall test dependencies:

```bash
pip install --upgrade -r tests/requirements.txt
```

### Mock Server Won't Start

Check if port 5001 is already in use:

```bash
# Windows
netstat -ano | findstr :5001

# Stop the process if needed
```

---

# 中文指南

> **多语言文档** | [English](#ha-ip-monitor---testing-guide) | [日本語](#日本語ガイド)

本指南说明如何运行HA IP Monitor集成的测试。

## 前置要求

### 所需软件
- Python 3.9 或更高版本
- pip（Python包管理器）

### 安装测试依赖

```bash
# 进入项目目录
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor

# 安装测试依赖
pip install -r tests/requirements.txt
```

## 运行测试

### 运行所有测试

```bash
# 运行所有单元测试
pytest

# 带详细输出运行
pytest -v

# 带覆盖率报告运行
pytest --cov=custom_components.ha_ip_monitor --cov-report=html
```

### 运行特定测试文件

```bash
# 仅测试协调器
pytest tests/test_coordinator.py

# 仅测试传感器
pytest tests/test_sensor.py

# 仅测试配置流程
pytest tests/test_config_flow.py
```

### 运行特定测试函数

```bash
# 运行特定测试函数
pytest tests/test_coordinator.py::test_coordinator_initialization

# 运行匹配模式的测试
pytest -k "test_sensor"
```

## 使用模拟API服务器

项目包含一个用于开发和测试的模拟VPS API服务器。

### 启动模拟服务器

```bash
# 启动模拟API服务器
python dev_tools/mock_vps_api.py
```

服务器将在 `http://localhost:5001` 启动，配置为：
- **API令牌**: `test-token-12345`
- **模拟数据**: 生成随机威胁数据

### 测试API端点

```bash
# 健康检查（无需认证）
curl http://localhost:5001/health

# 获取系统状态
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/status

# 获取威胁数据
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/threats
```

### 在Home Assistant中使用模拟服务器

1. 启动模拟API服务器
2. 使用以下配置设置HA IP Monitor集成：
   - VPS主机: `localhost` 或 `127.0.0.1`
   - API端口: `5001`
   - API令牌: `test-token-12345`
3. 集成将连接到模拟服务器而不是真实VPS

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # 共享fixtures和配置
├── test_coordinator.py      # 协调器测试（15个测试）
├── test_sensor.py           # 传感器实体测试（14个测试）
├── test_config_flow.py      # 配置流程测试（7个测试）
└── requirements.txt         # 测试依赖
```

## 测试覆盖率

当前测试覆盖率：
- **协调器**: 15个单元测试
- **传感器**: 14个单元测试
- **配置流程**: 7个单元测试
- **总计**: 36个单元测试

## 故障排查

### 导入错误

如果看到导入错误，确保你在项目根目录：

```bash
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor
```

### 依赖问题

重新安装测试依赖：

```bash
pip install --upgrade -r tests/requirements.txt
```

### 模拟服务器无法启动

检查端口5001是否已被占用：

```bash
# Windows
netstat -ano | findstr :5001

# 如需要，停止该进程
```

---

# 日本語ガイド

> **多言語ドキュメント** | [English](#ha-ip-monitor---testing-guide) | [中文](#中文指南)

本ガイドでは、HA IP Monitor統合のテストを実行する方法を説明します。

## 前提条件

### 必要なソフトウェア
- Python 3.9以上
- pip（Pythonパッケージマネージャー）

### テスト依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor

# テスト依存関係をインストール
pip install -r tests/requirements.txt
```

## テストの実行

### すべてのテストを実行

```bash
# すべてのユニットテストを実行
pytest

# 詳細な出力で実行
pytest -v

# カバレッジレポート付きで実行
pytest --cov=custom_components.ha_ip_monitor --cov-report=html
```

### 特定のテストファイルを実行

```bash
# コーディネーターのみテスト
pytest tests/test_coordinator.py

# センサーのみテスト
pytest tests/test_sensor.py

# 設定フローのみテスト
pytest tests/test_config_flow.py
```

### 特定のテスト関数を実行

```bash
# 特定のテスト関数を実行
pytest tests/test_coordinator.py::test_coordinator_initialization

# パターンに一致するテストを実行
pytest -k "test_sensor"
```

## モックAPIサーバーの使用

プロジェクトには、開発とテスト用のモックVPS APIサーバーが含まれています。

### モックサーバーを起動

```bash
# モックAPIサーバーを起動
python dev_tools/mock_vps_api.py
```

サーバーは `http://localhost:5001` で起動し、以下の設定になります：
- **APIトークン**: `test-token-12345`
- **モックデータ**: ランダムな脅威データが生成されます

### APIエンドポイントをテスト

```bash
# ヘルスチェック（認証不要）
curl http://localhost:5001/health

# システムステータスを取得
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/status

# 脅威データを取得
curl -H "Authorization: Bearer test-token-12345" http://localhost:5001/api/threats
```

### Home Assistantでモックサーバーを使用

1. モックAPIサーバーを起動
2. 以下の設定でHA IP Monitor統合を設定：
   - VPSホスト: `localhost` または `127.0.0.1`
   - APIポート: `5001`
   - APIトークン: `test-token-12345`
3. 統合は実際のVPSではなくモックサーバーに接続します

## テスト構造

```
tests/
├── __init__.py              # テストパッケージ初期化
├── conftest.py              # 共有フィクスチャと設定
├── test_coordinator.py      # コーディネーターテスト（15テスト）
├── test_sensor.py           # センサーエンティティテスト（14テスト）
├── test_config_flow.py      # 設定フローテスト（7テスト）
└── requirements.txt         # テスト依存関係
```

## テストカバレッジ

現在のテストカバレッジ：
- **コーディネーター**: 15ユニットテスト
- **センサー**: 14ユニットテスト
- **設定フロー**: 7ユニットテスト
- **合計**: 36ユニットテスト

## トラブルシューティング

### インポートエラー

インポートエラーが表示される場合は、プロジェクトのルートディレクトリにいることを確認してください：

```bash
cd C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor
```

### 依存関係の問題

テスト依存関係を再インストール：

```bash
pip install --upgrade -r tests/requirements.txt
```

### モックサーバーが起動しない

ポート5001が既に使用されているか確認：

```bash
# Windows
netstat -ano | findstr :5001

# 必要に応じてプロセスを停止
```
