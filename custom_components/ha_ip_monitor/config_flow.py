"""HA IP Monitor統合の設定フロー"""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_VPS_HOST,
    CONF_VPS_PORT,
    CONF_VPS_USERNAME,
    CONF_VPS_PASSWORD,
    CONF_VPS_SSH_KEY,
    CONF_API_PORT,
    CONF_API_TOKEN,
    CONF_USE_SSH_KEY,
    DEFAULT_VPS_PORT,
    DEFAULT_API_PORT,
)

_LOGGER = logging.getLogger(__name__)

# ステップ1: VPS接続設定のスキーマ
STEP_VPS_CONNECTION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VPS_HOST): cv.string,
        vol.Optional(CONF_VPS_PORT, default=DEFAULT_VPS_PORT): cv.port,
        vol.Required(CONF_VPS_USERNAME): cv.string,
        vol.Optional(CONF_USE_SSH_KEY, default=False): cv.boolean,
    }
)

# ステップ2: 認証設定のスキーマ
STEP_AUTH_PASSWORD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VPS_PASSWORD): cv.string,
    }
)

STEP_AUTH_KEY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VPS_SSH_KEY): cv.string,
    }
)

# ステップ3: API設定のスキーマ
STEP_API_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_API_PORT, default=DEFAULT_API_PORT): cv.port,
        vol.Required(CONF_API_TOKEN): cv.string,
    }
)


async def validate_vps_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """VPS接続を検証する"""
    # TODO: 実際のVPS接続テストを実装
    # - SSHで接続できるか確認
    # - 必要なコマンドが実行できるか確認

    # 仮の検証ロジック
    host = data.get(CONF_VPS_HOST)
    if not host:
        raise InvalidHost("VPSホストアドレスが無効です")

    # 接続成功を示す情報を返す
    return {"title": f"HA IP Monitor ({host})"}


async def validate_api_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """API接続を検証する"""
    # TODO: 実際のAPI接続テストを実装
    # - API エンドポイントにアクセスできるか確認
    # - API トークンが有効か確認

    # 仮の検証ロジック
    api_port = data.get(CONF_API_PORT, DEFAULT_API_PORT)
    _LOGGER.info(f"API接続を検証中: ポート {api_port}")

    return {"api_connected": True}


class HAIPMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """HA IP Monitor設定フローハンドラー"""

    VERSION = 1

    def __init__(self):
        """設定フローの初期化"""
        self.data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """ユーザーが開始した設定フロー"""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # VPS接続の検証
                info = await validate_vps_connection(self.hass, user_input)

                # データを保存
                self.data.update(user_input)

                # 次のステップへ: 認証方法によって分岐
                if user_input.get(CONF_USE_SSH_KEY):
                    return await self.async_step_ssh_key()
                else:
                    return await self.async_step_password()

            except InvalidHost:
                errors["base"] = "invalid_host"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("予期しないエラーが発生しました")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_VPS_CONNECTION_SCHEMA,
            errors=errors,
            description_placeholders={
                "example_host": "167.179.78.163",
            },
        )

    async def async_step_password(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """パスワード認証のステップ"""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # パスワードを保存
                self.data.update(user_input)

                # 次のステップへ: API設定
                return await self.async_step_api_config()

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("パスワード設定中にエラーが発生しました")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="password",
            data_schema=STEP_AUTH_PASSWORD_SCHEMA,
            errors=errors,
        )

    async def async_step_ssh_key(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """SSHキー認証のステップ"""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # SSHキーを保存
                self.data.update(user_input)

                # 次のステップへ: API設定
                return await self.async_step_api_config()

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("SSHキー設定中にエラーが発生しました")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="ssh_key",
            data_schema=STEP_AUTH_KEY_SCHEMA,
            errors=errors,
        )

    async def async_step_api_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """API設定のステップ"""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # API設定を保存
                self.data.update(user_input)

                # API接続の検証
                await validate_api_connection(self.hass, self.data)

                # 設定エントリーを作成
                return self.async_create_entry(
                    title=f"HA IP Monitor ({self.data[CONF_VPS_HOST]})",
                    data=self.data,
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("API設定中にエラーが発生しました")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="api_config",
            data_schema=STEP_API_CONFIG_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """接続できないエラー"""


class InvalidAuth(HomeAssistantError):
    """認証が無効なエラー"""


class InvalidHost(HomeAssistantError):
    """ホストが無効なエラー"""
