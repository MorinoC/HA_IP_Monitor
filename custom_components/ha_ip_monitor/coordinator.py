"""
ファイル名: coordinator.py
説明: VPSデータ更新コーディネーター
作成日: 2025-11-13
最終更新: 2025-11-13
"""
import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util import dt

from .const import (
    DOMAIN,
    CONF_VPS_HOST,
    CONF_API_PORT,
    CONF_API_TOKEN,
    DEFAULT_API_PORT,
    UPDATE_INTERVAL,
    TIMEOUT,
    API_ENDPOINT_STATUS,
    API_ENDPOINT_THREATS,
)

_LOGGER = logging.getLogger(__name__)


class HAIPMonitorDataUpdateCoordinator(DataUpdateCoordinator):
    """VPS監視データを管理するコーディネータークラス"""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """コーディネーターの初期化

        Args:
            hass: Home Assistantインスタンス
            entry: 設定エントリー
        """
        self.entry = entry
        self.hass = hass

        # 設定データの取得
        self.vps_host = entry.data.get(CONF_VPS_HOST)
        self.api_port = entry.data.get(CONF_API_PORT, DEFAULT_API_PORT)
        self.api_token = entry.data.get(CONF_API_TOKEN)

        # APIベースURLの構築
        self.api_base_url = f"http://{self.vps_host}:{self.api_port}"

        _LOGGER.info(
            f"コーディネーターを初期化しました - VPS: {self.vps_host}:{self.api_port}"
        )

        # 親クラスの初期化
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """データの更新を実行

        このメソッドは定期的に自動実行される

        Returns:
            dict: 更新されたデータ

        Raises:
            UpdateFailed: データ取得に失敗した場合
            ConfigEntryAuthFailed: 認証に失敗した場合
        """
        _LOGGER.debug("VPSデータの更新を開始します")

        try:
            # VPSステータスと脅威データを並行取得
            async with async_timeout.timeout(TIMEOUT):
                status_data = await self._fetch_vps_status()
                threats_data = await self._fetch_threats()

            # データを統合して返す
            updated_data = {
                "status": status_data,
                "threats": threats_data,
                "last_update": dt.utcnow().isoformat(),
            }

            _LOGGER.debug(f"データ更新成功: {len(threats_data.get('threat_list', []))}件の脅威")
            return updated_data

        except aiohttp.ClientError as err:
            _LOGGER.error(f"VPS API通信エラー: {err}")
            raise UpdateFailed(f"VPS通信に失敗しました: {err}")
        except asyncio.TimeoutError:
            _LOGGER.error(f"VPS API接続タイムアウト ({TIMEOUT}秒)")
            raise UpdateFailed("VPS接続がタイムアウトしました")
        except Exception as err:
            _LOGGER.exception(f"予期しないエラーが発生しました: {err}")
            raise UpdateFailed(f"データ更新エラー: {err}")

    async def _fetch_vps_status(self) -> dict[str, Any]:
        """VPSシステムステータスを取得

        Returns:
            dict: システムステータスデータ
        """
        url = f"{self.api_base_url}{API_ENDPOINT_STATUS}"
        data = await self._make_api_request(url)

        # デフォルト値を含むステータスデータを返す
        return {
            "blocked_ips_today": data.get("blocked_ips_today", 0),
            "ssh_attacks_today": data.get("ssh_attacks_today", 0),
            "vpn_attacks_today": data.get("vpn_attacks_today", 0),
            "firewall_rules_count": data.get("firewall_rules_count", 0),
            "system_status": data.get("system_status", "unknown"),
            "cpu_usage": data.get("cpu_usage", 0),
            "memory_usage": data.get("memory_usage", 0),
            "uptime": data.get("uptime", "unknown"),
        }

    async def _fetch_threats(self) -> dict[str, Any]:
        """脅威データを取得

        Returns:
            dict: 脅威データ（IPリスト、統計など）
        """
        url = f"{self.api_base_url}{API_ENDPOINT_THREATS}"
        data = await self._make_api_request(url)

        # デフォルト値を含む脅威データを返す
        return {
            "threat_level": data.get("threat_level", "low"),
            "total_threats": data.get("total_threats", 0),
            "threat_list": data.get("threat_list", []),
            "top_attack_countries": data.get("top_attack_countries", []),
            "attack_trend": data.get("attack_trend", []),
        }

    async def _make_api_request(self, url: str, method: str = "GET",
                                json_data: dict = None) -> dict[str, Any]:
        """VPS APIへのHTTPリクエストを実行

        Args:
            url: リクエストURL
            method: HTTPメソッド (GET, POST, etc.)
            json_data: POSTデータ（オプション）

        Returns:
            dict: APIレスポンスのJSONデータ

        Raises:
            ConfigEntryAuthFailed: 認証エラー（401, 403）
            UpdateFailed: その他のAPIエラー
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        _LOGGER.debug(f"API リクエスト: {method} {url}")

        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await self._handle_response(response)
                elif method == "POST":
                    async with session.post(url, headers=headers, json=json_data) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"サポートされていないHTTPメソッド: {method}")

        except aiohttp.ClientError as err:
            _LOGGER.error(f"HTTP リクエストエラー: {err}")
            raise UpdateFailed(f"API通信エラー: {err}")

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        """APIレスポンスを処理

        Args:
            response: aiohttpレスポンスオブジェクト

        Returns:
            dict: パースされたJSONデータ

        Raises:
            ConfigEntryAuthFailed: 認証エラー
            UpdateFailed: その他のエラー
        """
        if response.status == 401:
            _LOGGER.error("API認証エラー: トークンが無効です")
            raise ConfigEntryAuthFailed("APIトークンが無効です")

        if response.status == 403:
            _LOGGER.error("API認証エラー: アクセスが拒否されました")
            raise ConfigEntryAuthFailed("APIアクセスが拒否されました")

        if response.status != 200:
            error_text = await response.text()
            _LOGGER.error(f"APIエラー {response.status}: {error_text}")
            raise UpdateFailed(f"API エラー ({response.status}): {error_text}")

        try:
            data = await response.json()
            _LOGGER.debug(f"API レスポンス成功: {response.status}")
            return data
        except Exception as err:
            _LOGGER.error(f"JSONパースエラー: {err}")
            raise UpdateFailed(f"レスポンスのパースに失敗しました: {err}")

    async def async_block_ip(self, ip_address: str, duration: int = None) -> bool:
        """IPアドレスをブロック

        Args:
            ip_address: ブロックするIPアドレス
            duration: ブロック期間（秒、Noneの場合は永久）

        Returns:
            bool: 成功した場合True
        """
        from .const import API_ENDPOINT_BLOCK_IP

        url = f"{self.api_base_url}{API_ENDPOINT_BLOCK_IP}"
        json_data = {"ip_address": ip_address}

        if duration is not None:
            json_data["duration"] = duration

        try:
            _LOGGER.info(f"IPブロック要求: {ip_address}")
            result = await self._make_api_request(url, method="POST", json_data=json_data)

            if result.get("success"):
                _LOGGER.info(f"IP {ip_address} をブロックしました")
                # データを即座に更新
                await self.async_request_refresh()
                return True
            else:
                _LOGGER.error(f"IPブロック失敗: {result.get('error')}")
                return False

        except Exception as err:
            _LOGGER.error(f"IPブロックエラー: {err}")
            return False

    async def async_unblock_ip(self, ip_address: str) -> bool:
        """IPアドレスのブロックを解除

        Args:
            ip_address: ブロック解除するIPアドレス

        Returns:
            bool: 成功した場合True
        """
        from .const import API_ENDPOINT_UNBLOCK_IP

        url = f"{self.api_base_url}{API_ENDPOINT_UNBLOCK_IP}"
        json_data = {"ip_address": ip_address}

        try:
            _LOGGER.info(f"IPブロック解除要求: {ip_address}")
            result = await self._make_api_request(url, method="POST", json_data=json_data)

            if result.get("success"):
                _LOGGER.info(f"IP {ip_address} のブロックを解除しました")
                # データを即座に更新
                await self.async_request_refresh()
                return True
            else:
                _LOGGER.error(f"IPブロック解除失敗: {result.get('error')}")
                return False

        except Exception as err:
            _LOGGER.error(f"IPブロック解除エラー: {err}")
            return False
