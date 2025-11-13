"""HA IP Monitor統合のメインエントリーポイント"""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import HAIPMonitorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# サービススキーマの定義
SERVICE_BLOCK_IP = "block_ip"
SERVICE_UNBLOCK_IP = "unblock_ip"
SERVICE_EMERGENCY_LOCKDOWN = "emergency_lockdown"

ATTR_IP_ADDRESS = "ip_address"
ATTR_DURATION = "duration"
ATTR_REASON = "reason"

SERVICE_BLOCK_IP_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_IP_ADDRESS): cv.string,
        vol.Optional(ATTR_DURATION): cv.positive_int,
    }
)

SERVICE_UNBLOCK_IP_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_IP_ADDRESS): cv.string,
    }
)

SERVICE_EMERGENCY_LOCKDOWN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_REASON): cv.string,
    }
)

# 使用するプラットフォームのリスト
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """統合のセットアップ（設定エントリーから）"""
    _LOGGER.info("HA IP Monitor統合のセットアップを開始します")

    # ドメインデータの初期化
    hass.data.setdefault(DOMAIN, {})

    # データコーディネーターの作成
    coordinator = HAIPMonitorDataUpdateCoordinator(hass, entry)

    # 初回データ取得を実行
    await coordinator.async_config_entry_first_refresh()

    # エントリーデータに保存
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # プラットフォームのセットアップ
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # サービスの登録
    await async_setup_services(hass, entry)

    _LOGGER.info("HA IP Monitor統合のセットアップが完了しました")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """統合のアンロード"""
    _LOGGER.info("HA IP Monitor統合をアンロードします")

    # プラットフォームのアンロード
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # データのクリーンアップ
        hass.data[DOMAIN].pop(entry.entry_id)

        # 最後のエントリーの場合、サービスを削除
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_BLOCK_IP)
            hass.services.async_remove(DOMAIN, SERVICE_UNBLOCK_IP)
            hass.services.async_remove(DOMAIN, SERVICE_EMERGENCY_LOCKDOWN)
            _LOGGER.info("已注销所有HA IP Monitor服务")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """統合の再読み込み"""
    _LOGGER.info("HA IP Monitor統合を再読み込みします")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """サービスのセットアップ"""

    async def handle_block_ip(call: ServiceCall) -> None:
        """IPアドレス封禁サービスの処理"""
        ip_address = call.data.get(ATTR_IP_ADDRESS)
        duration = call.data.get(ATTR_DURATION)

        _LOGGER.info(f"正在封禁IP地址: {ip_address}")

        # すべてのコーディネーターを取得
        coordinators = hass.data[DOMAIN]

        # 各エントリーのコーディネーターを通じてIPを封禁
        for entry_id, coordinator in coordinators.items():
            if isinstance(coordinator, HAIPMonitorDataUpdateCoordinator):
                try:
                    await coordinator.async_block_ip(ip_address)
                    _LOGGER.info(f"成功封禁IP地址: {ip_address}")

                    # データを更新して状態を反映
                    await coordinator.async_request_refresh()

                except Exception as err:
                    _LOGGER.error(f"封禁IP地址失败: {ip_address} - {err}")
                    raise HomeAssistantError(f"封禁IP地址失败: {err}") from err

    async def handle_unblock_ip(call: ServiceCall) -> None:
        """IPアドレス解封サービスの処理"""
        ip_address = call.data.get(ATTR_IP_ADDRESS)

        _LOGGER.info(f"正在解封IP地址: {ip_address}")

        # すべてのコーディネーターを取得
        coordinators = hass.data[DOMAIN]

        # 各エントリーのコーディネーターを通じてIPを解封
        for entry_id, coordinator in coordinators.items():
            if isinstance(coordinator, HAIPMonitorDataUpdateCoordinator):
                try:
                    await coordinator.async_unblock_ip(ip_address)
                    _LOGGER.info(f"成功解封IP地址: {ip_address}")

                    # データを更新して状態を反映
                    await coordinator.async_request_refresh()

                except Exception as err:
                    _LOGGER.error(f"解封IP地址失败: {ip_address} - {err}")
                    raise HomeAssistantError(f"解封IP地址失败: {err}") from err

    async def handle_emergency_lockdown(call: ServiceCall) -> None:
        """緊急ロックダウンサービスの処理"""
        reason = call.data.get(ATTR_REASON, "手动触发紧急锁定")

        _LOGGER.warning(f"正在启动紧急锁定模式: {reason}")

        # すべてのコーディネーターを取得
        coordinators = hass.data[DOMAIN]

        # 各エントリーのコーディネーターを通じて緊急ロックダウンを実行
        for entry_id, coordinator in coordinators.items():
            if isinstance(coordinator, HAIPMonitorDataUpdateCoordinator):
                try:
                    await coordinator.async_emergency_lockdown(reason)
                    _LOGGER.warning(f"紧急锁定模式已启动")

                    # データを更新して状態を反映
                    await coordinator.async_request_refresh()

                except Exception as err:
                    _LOGGER.error(f"启动紧急锁定失败: {err}")
                    raise HomeAssistantError(f"启动紧急锁定失败: {err}") from err

    # サービスの登録
    hass.services.async_register(
        DOMAIN,
        SERVICE_BLOCK_IP,
        handle_block_ip,
        schema=SERVICE_BLOCK_IP_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UNBLOCK_IP,
        handle_unblock_ip,
        schema=SERVICE_UNBLOCK_IP_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EMERGENCY_LOCKDOWN,
        handle_emergency_lockdown,
        schema=SERVICE_EMERGENCY_LOCKDOWN_SCHEMA,
    )

    _LOGGER.info("已注册所有HA IP Monitor服务")
