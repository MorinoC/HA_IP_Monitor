"""
ファイル名: conftest.py
説明: pytestの共通フィクスチャと設定
作成日: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.ha_ip_monitor.const import (
    DOMAIN,
    CONF_VPS_HOST,
    CONF_VPS_PORT,
    CONF_VPS_USERNAME,
    CONF_API_PORT,
    CONF_API_TOKEN,
    DEFAULT_VPS_PORT,
    DEFAULT_API_PORT,
)


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """モックConfigEntryを作成"""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="HA IP Monitor (192.168.1.100)",
        data={
            CONF_VPS_HOST: "192.168.1.100",
            CONF_VPS_PORT: DEFAULT_VPS_PORT,
            CONF_VPS_USERNAME: "testuser",
            CONF_API_PORT: DEFAULT_API_PORT,
            CONF_API_TOKEN: "test-token-12345",
        },
        source="user",
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_hass() -> HomeAssistant:
    """モックHome Assistantインスタンスを作成"""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.helpers = MagicMock()
    return hass


@pytest.fixture
def mock_api_response_status():
    """モックAPIレスポンス（status）を作成"""
    return {
        "blocked_ips_today": 15,
        "ssh_attacks_today": 234,
        "vpn_attacks_today": 45,
        "firewall_rules_count": 28,
        "system_status": "online",
        "cpu_usage": 25.5,
        "memory_usage": 48.2,
        "uptime": "15 days, 3:24:10",
    }


@pytest.fixture
def mock_api_response_threats():
    """モックAPIレスポンス（threats）を作成"""
    return {
        "threat_level": "high",
        "total_threats": 42,
        "threat_list": [
            {
                "ip_address": "185.200.116.43",
                "country": "CN",
                "attack_count": 156,
                "threat_level": "critical",
                "last_attack_time": "2025-11-13T10:30:00Z",
                "blocked": True,
            },
            {
                "ip_address": "207.90.244.11",
                "country": "US",
                "attack_count": 23,
                "threat_level": "medium",
                "last_attack_time": "2025-11-13T09:15:00Z",
                "blocked": False,
            },
        ],
        "top_attack_countries": [
            {"country": "CN", "count": 156},
            {"country": "US", "count": 78},
            {"country": "RU", "count": 45},
        ],
        "attack_trend": [10, 15, 20, 25, 30],
    }


@pytest.fixture
def mock_aiohttp_session():
    """モックaiohttpセッションを作成"""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock()

    # getとpostメソッドのモック
    session.get = AsyncMock(return_value=response)
    session.post = AsyncMock(return_value=response)

    return session, response
