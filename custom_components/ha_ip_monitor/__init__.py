"""HA IP Monitor統合のメインエントリーポイント"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HAIPMonitorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

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

    # TODO: サービスの登録（後で実装）
    # await async_setup_services(hass)

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

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """統合の再読み込み"""
    _LOGGER.info("HA IP Monitor統合を再読み込みします")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
