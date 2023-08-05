from flask_restplus import Api
from micropydd.actions import Action


class GetPostmanAction(Action):

    def __init__(self, api: Api):
        super().__init__()
        self.api = api

    def execute(self, *args, **kwargs):
        return self.api.as_postman(urlvars=False, swagger=True)
