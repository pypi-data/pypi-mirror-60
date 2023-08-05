from typing import Dict

from flask import Flask
from flask_restplus import Api
from micropydd.config import Config
from micropydd.module import MicroPyDDModule

from micropydd_restplus.actions import GetPostmanAction
from micropydd_restplus.config import RestplusConfig
from micropydd_restplus.rest import RestService
from micropydd_restplus.utils import base_resources


class MicroPyDDRestplusModule(MicroPyDDModule):

    def __init__(self, config_mapping: Dict) -> None:
        super().__init__()
        self._config_mapping = config_mapping

    def context(self, existing_context: Dict) -> Dict:
        super().context(existing_context)
        result = {
            RestplusConfig: existing_context[Config] if isinstance(existing_context[Config], RestplusConfig) else None,

            Flask: Flask(__name__)
        }

        result[Api] = Api(
            title=result[RestplusConfig].REST_API_NAME,
            version=result[RestplusConfig].REST_API_VERSION,
            description=result[RestplusConfig].REST_API_DESCRIPTION,
        )
        result[Api].init_app(result[Flask])

        result[RestplusConfig] = RestService(result[Api], result[RestplusConfig])
        result[RestplusConfig].register(base_resources())

        result[GetPostmanAction] = GetPostmanAction(result[Api])

        return result
