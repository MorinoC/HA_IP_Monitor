"""
ファイル名: sensor.py
説明: HA IP Monitor センサープラットフォーム
作成日: 2025-11-13
最終更新: 2025-11-13
"""
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_BLOCKED_IPS_TODAY,
    SENSOR_SSH_ATTACKS_TODAY,
    SENSOR_VPN_ATTACKS_TODAY,
    SENSOR_VPS_SYSTEM_STATUS,
    SENSOR_CURRENT_THREAT_LEVEL,
    THREAT_LEVEL_LOW,
    THREAT_LEVEL_MEDIUM,
    THREAT_LEVEL_HIGH,
    THREAT_LEVEL_CRITICAL,
)
from .coordinator import HAIPMonitorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """センサープラットフォームのセットアップ

    Args:
        hass: Home Assistantインスタンス
        entry: 設定エントリー
        async_add_entities: エンティティ追加用コールバック
    """
    _LOGGER.info("HA IP Monitor センサーをセットアップします")

    # コーディネーターの取得
    coordinator: HAIPMonitorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # センサーエンティティのリストを作成
    sensors = [
        HAIPMonitorBlockedIPsSensor(coordinator, entry),
        HAIPMonitorSSHAttacksSensor(coordinator, entry),
        HAIPMonitorVPNAttacksSensor(coordinator, entry),
        HAIPMonitorSystemStatusSensor(coordinator, entry),
        HAIPMonitorThreatLevelSensor(coordinator, entry),
    ]

    # エンティティを追加
    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info(f"{len(sensors)}個のセンサーを追加しました")


class HAIPMonitorSensorBase(CoordinatorEntity, SensorEntity):
    """HA IP Monitor センサーの基底クラス"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """基底センサーの初期化

        Args:
            coordinator: データコーディネーター
            entry: 設定エントリー
        """
        super().__init__(coordinator)
        self.entry = entry

        # デバイス情報の設定
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "HA IP Monitor",
            "manufacturer": "HA IP Monitor Project",
            "model": "VPS Security Monitor",
            "sw_version": "0.2.0",
        }


class HAIPMonitorBlockedIPsSensor(HAIPMonitorSensorBase):
    """ブロックされたIP数センサー"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """センサーの初期化"""
        super().__init__(coordinator, entry)

        # センサー固有の設定
        self._attr_name = "今日ブロックしたIP数"
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_BLOCKED_IPS_TODAY}"
        self._attr_icon = "mdi:shield-lock"
        self._attr_native_unit_of_measurement = "個"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int:
        """センサーの現在値を返す"""
        if self.coordinator.data is None:
            return 0

        status = self.coordinator.data.get("status", {})
        return status.get("blocked_ips_today", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """追加の状態属性を返す"""
        if self.coordinator.data is None:
            return {}

        threats = self.coordinator.data.get("threats", {})
        threat_list = threats.get("threat_list", [])

        # 最近ブロックされたIPのリスト（最大5件）
        recent_blocked_ips = [
            {
                "ip": threat.get("ip_address"),
                "country": threat.get("country"),
                "attacks": threat.get("attack_count"),
            }
            for threat in threat_list[:5]
            if threat.get("blocked", False)
        ]

        return {
            "recent_blocked_ips": recent_blocked_ips,
            "last_update": self.coordinator.data.get("last_update"),
        }


class HAIPMonitorSSHAttacksSensor(HAIPMonitorSensorBase):
    """SSH攻撃回数センサー"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """センサーの初期化"""
        super().__init__(coordinator, entry)

        self._attr_name = "今日のSSH攻撃回数"
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_SSH_ATTACKS_TODAY}"
        self._attr_icon = "mdi:alert-circle"
        self._attr_native_unit_of_measurement = "回"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int:
        """センサーの現在値を返す"""
        if self.coordinator.data is None:
            return 0

        status = self.coordinator.data.get("status", {})
        return status.get("ssh_attacks_today", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """追加の状態属性を返す"""
        if self.coordinator.data is None:
            return {}

        threats = self.coordinator.data.get("threats", {})

        return {
            "attack_trend": threats.get("attack_trend", []),
            "top_countries": threats.get("top_attack_countries", []),
            "last_update": self.coordinator.data.get("last_update"),
        }


class HAIPMonitorVPNAttacksSensor(HAIPMonitorSensorBase):
    """VPN攻撃回数センサー"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """センサーの初期化"""
        super().__init__(coordinator, entry)

        self._attr_name = "今日のVPN攻撃回数"
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_VPN_ATTACKS_TODAY}"
        self._attr_icon = "mdi:vpn"
        self._attr_native_unit_of_measurement = "回"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int:
        """センサーの現在値を返す"""
        if self.coordinator.data is None:
            return 0

        status = self.coordinator.data.get("status", {})
        return status.get("vpn_attacks_today", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """追加の状態属性を返す"""
        if self.coordinator.data is None:
            return {}

        return {
            "last_update": self.coordinator.data.get("last_update"),
        }


class HAIPMonitorSystemStatusSensor(HAIPMonitorSensorBase):
    """VPSシステムステータスセンサー"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """センサーの初期化"""
        super().__init__(coordinator, entry)

        self._attr_name = "VPSシステムステータス"
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_VPS_SYSTEM_STATUS}"
        self._attr_icon = "mdi:server"

    @property
    def native_value(self) -> str:
        """センサーの現在値を返す"""
        if self.coordinator.data is None:
            return "unknown"

        status = self.coordinator.data.get("status", {})
        return status.get("system_status", "unknown")

    @property
    def icon(self) -> str:
        """ステータスに応じたアイコンを返す"""
        status = self.native_value

        if status == "online":
            return "mdi:server-network"
        elif status == "warning":
            return "mdi:server-network-off"
        elif status == "error":
            return "mdi:server-remove"
        else:
            return "mdi:server"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """追加の状態属性を返す"""
        if self.coordinator.data is None:
            return {}

        status = self.coordinator.data.get("status", {})

        return {
            "cpu_usage": status.get("cpu_usage", 0),
            "memory_usage": status.get("memory_usage", 0),
            "uptime": status.get("uptime", "unknown"),
            "firewall_rules": status.get("firewall_rules_count", 0),
            "vps_host": self.coordinator.vps_host,
            "last_update": self.coordinator.data.get("last_update"),
        }


class HAIPMonitorThreatLevelSensor(HAIPMonitorSensorBase):
    """現在の脅威レベルセンサー"""

    def __init__(
        self,
        coordinator: HAIPMonitorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """センサーの初期化"""
        super().__init__(coordinator, entry)

        self._attr_name = "現在の脅威レベル"
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_CURRENT_THREAT_LEVEL}"

    @property
    def native_value(self) -> str:
        """センサーの現在値を返す"""
        if self.coordinator.data is None:
            return THREAT_LEVEL_LOW

        threats = self.coordinator.data.get("threats", {})
        return threats.get("threat_level", THREAT_LEVEL_LOW)

    @property
    def icon(self) -> str:
        """脅威レベルに応じたアイコンを返す"""
        threat_level = self.native_value

        if threat_level == THREAT_LEVEL_CRITICAL:
            return "mdi:shield-alert"
        elif threat_level == THREAT_LEVEL_HIGH:
            return "mdi:shield-remove"
        elif threat_level == THREAT_LEVEL_MEDIUM:
            return "mdi:shield-half-full"
        else:
            return "mdi:shield-check"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """追加の状態属性を返す"""
        if self.coordinator.data is None:
            return {}

        threats = self.coordinator.data.get("threats", {})
        threat_list = threats.get("threat_list", [])

        # 脅威レベル別のカウント
        threat_counts = {
            THREAT_LEVEL_LOW: 0,
            THREAT_LEVEL_MEDIUM: 0,
            THREAT_LEVEL_HIGH: 0,
            THREAT_LEVEL_CRITICAL: 0,
        }

        for threat in threat_list:
            level = threat.get("threat_level", THREAT_LEVEL_LOW)
            if level in threat_counts:
                threat_counts[level] += 1

        return {
            "total_threats": threats.get("total_threats", 0),
            "threat_distribution": threat_counts,
            "top_countries": threats.get("top_attack_countries", []),
            "last_update": self.coordinator.data.get("last_update"),
        }
