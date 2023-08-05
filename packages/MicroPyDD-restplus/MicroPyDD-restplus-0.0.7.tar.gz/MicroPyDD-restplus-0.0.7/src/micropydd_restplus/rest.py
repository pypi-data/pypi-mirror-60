from typing import List

from flask_restplus import Api, Namespace

from micropydd_restplus.config import RestplusConfig


class RestService:
    """
    Rest service
    """

    def __init__(self, api: Api, config: RestplusConfig):
        super().__init__()
        self.api = api
        self.config = config

    def register(self, namespaces: List[Namespace]):
        """
        Register namesapeces into the main API
        :param namespaces:
        :return:
        """
        for namespace in namespaces:
            self.api.add_namespace(ns=namespace, path=f'{self.config.REST_ROOT}/{namespace.name}')
