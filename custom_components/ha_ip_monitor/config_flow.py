"""HA IP Monitor統合の設定フロー"""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_VPS_HOST,
    CONF_API_PORT,
    CONF_API_TOKEN,
    DEFAULT_API_PORT,
)

_LOGGER = logging.getLogger(__name__)

# 简化的配置Schema - 只需要API连接信息
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VPS_HOST): cv.string,
        vol.Optional(CONF_API_PORT, default=DEFAULT_API_PORT): cv.port,
        vol.Required(CONF_API_TOKEN): cv.string,
    }
)


async def validate_api_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """API接続を検証する"""
    host = data.get(CONF_VPS_HOST)
    port = data.get(CONF_API_PORT, DEFAULT_API_PORT)
    token = data.get(CONF_API_TOKEN)

    if not host:
        raise InvalidHost("VPS主机地址无效")

    if not token:
        raise InvalidAuth("API Token无效")

    # 测试API连接
    url = f"http://{host}:{port}/health"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    _LOGGER.info(f"API连接成功: {host}:{port}")
                    return {"title": f"HA IP Monitor ({host})"}
                else:
                    raise CannotConnect(f"API返回错误状态码: {response.status}")
    except aiohttp.ClientError as err:
        _LOGGER.error(f"无法连接到API: {err}")
        raise CannotConnect(f"无法连接到VPS API: {err}") from err
    except Exception as err:
        _LOGGER.exception("API连接验证失败")
        raise CannotConnect(f"连接失败: {err}") from err


class HAIPMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """HA IP Monitor設定フローハンドラー"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """用户启动的配置流程"""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # 验证API连接
                info = await validate_api_connection(self.hass, user_input)

                # 创建配置条目
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

            except InvalidHost:
                errors["base"] = "invalid_host"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("配置过程中发生错误")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "example_host": "10.0.0.1",
                "example_port": "5001",
            },
        )


class CannotConnect(HomeAssistantError):
    """接続できないエラー"""


class InvalidAuth(HomeAssistantError):
    """認証が無効なエラー"""


class InvalidHost(HomeAssistantError):
    """ホストが無効なエラー"""
