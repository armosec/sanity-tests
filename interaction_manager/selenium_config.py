from __future__ import annotations

from ast import literal_eval
from logging import getLogger
from os import environ

from attr import dataclass

_logger = getLogger(__name__)


@dataclass
class InteractionManagerConfig:
    headless: bool
    timeout: int

    @classmethod
    def from_env(cls) -> InteractionManagerConfig:
        config = InteractionManagerConfig(
            headless=literal_eval(environ.get('IM_HEADLESS').title()) if environ.get('IM_HEADLESS') else False,
            timeout=int(environ['IM_TIMEOUT']) if environ.get('IM_TIMEOUT') else 15
        )

        _logger.info(
            f'Got interaction manager configuration from environment. {config}')

        return config
