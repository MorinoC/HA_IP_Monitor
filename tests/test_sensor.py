"""
ファイル名: test_sensor.py
説明: センサーエンティティのユニットテスト
作成日: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.ha_ip_monitor.sensor import (
    HAIPMonitorBlockedIPsSensor,
    HAIPMonitorSSHAttacksSensor,
    HAIPMonitorVPNAttacksSensor,
    HAIPMonitorSystemStatusSensor,
    HAIPMonitorThreatLevelSensor,
)
from custom_components.ha_ip_monitor.const import (
    THREAT_LEVEL_LOW,
    THREAT_LEVEL_HIGH,
    THREAT_LEVEL_CRITICAL,
)


@pytest.fixture
def mock_coordinator(mock_hass, mock_config_entry):
    """モックコーディネーターを作成"""
    coordinator = MagicMock()
    coordinator.hass = mock_hass
    coordinator.data = {
        "status": {
            "blocked_ips_today": 15,
            "ssh_attacks_today": 234,
            "vpn_attacks_today": 45,
            "firewall_rules_count": 28,
            "system_status": "online",
            "cpu_usage": 25.5,
            "memory_usage": 48.2,
            "uptime": "15 days, 3:24:10",
        },
        "threats": {
            "threat_level": "high",
            "total_threats": 42,
            "threat_list": [
                {
                    "ip_address": "185.200.116.43",
                    "country": "CN",
                    "attack_count": 156,
                    "threat_level": "critical",
                    "blocked": True,
                },
                {
                    "ip_address": "207.90.244.11",
                    "country": "US",
                    "attack_count": 23,
                    "threat_level": "medium",
                    "blocked": False,
                },
            ],
            "top_attack_countries": [
                {"country": "CN", "count": 156},
                {"country": "US", "count": 78},
            ],
            "attack_trend": [10, 15, 20, 25, 30],
        },
        "last_update": "2025-11-13T10:30:00Z",
    }
    coordinator.vps_host = "192.168.1.100"
    return coordinator


@pytest.mark.unit
def test_blocked_ips_sensor_initialization(mock_coordinator, mock_config_entry):
    """被阻止IPセンサーの初期化をテスト"""
    sensor = HAIPMonitorBlockedIPsSensor(mock_coordinator, mock_config_entry)

    assert sensor.coordinator == mock_coordinator
    assert "今日ブロックしたIP数" in sensor.name
    assert sensor.icon == "mdi:shield-lock"
    assert sensor.native_unit_of_measurement == "個"


@pytest.mark.unit
def test_blocked_ips_sensor_value(mock_coordinator, mock_config_entry):
    """被阻止IPセンサーの値をテスト"""
    sensor = HAIPMonitorBlockedIPsSensor(mock_coordinator, mock_config_entry)

    assert sensor.native_value == 15


@pytest.mark.unit
def test_blocked_ips_sensor_attributes(mock_coordinator, mock_config_entry):
    """被阻止IPセンサーの追加属性をテスト"""
    sensor = HAIPMonitorBlockedIPsSensor(mock_coordinator, mock_config_entry)

    attributes = sensor.extra_state_attributes

    assert "recent_blocked_ips" in attributes
    assert "last_update" in attributes
    assert len(attributes["recent_blocked_ips"]) == 1  # 1つだけブロック済み
    assert attributes["recent_blocked_ips"][0]["ip"] == "185.200.116.43"


@pytest.mark.unit
def test_ssh_attacks_sensor_value(mock_coordinator, mock_config_entry):
    """SSH攻撃センサーの値をテスト"""
    sensor = HAIPMonitorSSHAttacksSensor(mock_coordinator, mock_config_entry)

    assert sensor.native_value == 234
    assert sensor.icon == "mdi:alert-circle"
    assert sensor.native_unit_of_measurement == "回"


@pytest.mark.unit
def test_ssh_attacks_sensor_attributes(mock_coordinator, mock_config_entry):
    """SSH攻撃センサーの追加属性をテスト"""
    sensor = HAIPMonitorSSHAttacksSensor(mock_coordinator, mock_config_entry)

    attributes = sensor.extra_state_attributes

    assert "attack_trend" in attributes
    assert "top_countries" in attributes
    assert attributes["attack_trend"] == [10, 15, 20, 25, 30]


@pytest.mark.unit
def test_vpn_attacks_sensor_value(mock_coordinator, mock_config_entry):
    """VPN攻撃センサーの値をテスト"""
    sensor = HAIPMonitorVPNAttacksSensor(mock_coordinator, mock_config_entry)

    assert sensor.native_value == 45
    assert sensor.icon == "mdi:vpn"


@pytest.mark.unit
def test_system_status_sensor_value(mock_coordinator, mock_config_entry):
    """システムステータスセンサーの値をテスト"""
    sensor = HAIPMonitorSystemStatusSensor(mock_coordinator, mock_config_entry)

    assert sensor.native_value == "online"


@pytest.mark.unit
def test_system_status_sensor_icon(mock_coordinator, mock_config_entry):
    """システムステータスセンサーのアイコンをテスト"""
    sensor = HAIPMonitorSystemStatusSensor(mock_coordinator, mock_config_entry)

    # オンライン状態のアイコン
    assert sensor.icon == "mdi:server-network"

    # ステータスを変更してテスト
    mock_coordinator.data["status"]["system_status"] = "warning"
    assert sensor.icon == "mdi:server-network-off"

    mock_coordinator.data["status"]["system_status"] = "error"
    assert sensor.icon == "mdi:server-remove"


@pytest.mark.unit
def test_system_status_sensor_attributes(mock_coordinator, mock_config_entry):
    """システムステータスセンサーの追加属性をテスト"""
    sensor = HAIPMonitorSystemStatusSensor(mock_coordinator, mock_config_entry)

    attributes = sensor.extra_state_attributes

    assert attributes["cpu_usage"] == 25.5
    assert attributes["memory_usage"] == 48.2
    assert attributes["uptime"] == "15 days, 3:24:10"
    assert attributes["firewall_rules"] == 28
    assert attributes["vps_host"] == "192.168.1.100"


@pytest.mark.unit
def test_threat_level_sensor_value(mock_coordinator, mock_config_entry):
    """脅威レベルセンサーの値をテスト"""
    sensor = HAIPMonitorThreatLevelSensor(mock_coordinator, mock_config_entry)

    assert sensor.native_value == "high"


@pytest.mark.unit
def test_threat_level_sensor_icon(mock_coordinator, mock_config_entry):
    """脅威レベルセンサーのアイコンをテスト"""
    sensor = HAIPMonitorThreatLevelSensor(mock_coordinator, mock_config_entry)

    # 高レベルのアイコン
    assert sensor.icon == "mdi:shield-remove"

    # 重大レベル
    mock_coordinator.data["threats"]["threat_level"] = THREAT_LEVEL_CRITICAL
    assert sensor.icon == "mdi:shield-alert"

    # 低レベル
    mock_coordinator.data["threats"]["threat_level"] = THREAT_LEVEL_LOW
    assert sensor.icon == "mdi:shield-check"


@pytest.mark.unit
def test_threat_level_sensor_attributes(mock_coordinator, mock_config_entry):
    """脅威レベルセンサーの追加属性をテスト"""
    sensor = HAIPMonitorThreatLevelSensor(mock_coordinator, mock_config_entry)

    attributes = sensor.extra_state_attributes

    assert attributes["total_threats"] == 42
    assert "threat_distribution" in attributes
    assert "top_countries" in attributes


@pytest.mark.unit
def test_sensor_with_no_data(mock_coordinator, mock_config_entry):
    """データがない場合のセンサーをテスト"""
    mock_coordinator.data = None

    sensor = HAIPMonitorBlockedIPsSensor(mock_coordinator, mock_config_entry)

    # デフォルト値を返すべき
    assert sensor.native_value == 0
    assert sensor.extra_state_attributes == {}


@pytest.mark.unit
def test_sensor_device_info(mock_coordinator, mock_config_entry):
    """センサーのデバイス情報をテスト"""
    sensor = HAIPMonitorBlockedIPsSensor(mock_coordinator, mock_config_entry)

    device_info = sensor.device_info

    assert "identifiers" in device_info
    assert "name" in device_info
    assert device_info["name"] == "HA IP Monitor"
    assert device_info["manufacturer"] == "HA IP Monitor Project"
