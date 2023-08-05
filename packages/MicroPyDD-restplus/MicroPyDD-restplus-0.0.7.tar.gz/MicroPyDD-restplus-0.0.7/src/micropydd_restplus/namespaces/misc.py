from flask_restplus import Resource, fields, Namespace
from micropydd.actions import GetConfigAction, GetVersionAction

from micropydd_restplus.actions import GetPostmanAction
from micropydd_restplus.decorators import inject_actions

misc_ns = Namespace('misc', description='Utility endpoints')

status_fields = misc_ns.model('HealthCheck', {
    'status': fields.String,
})


@misc_ns.route('/postman')
class Postman(Resource):

    @inject_actions
    def get(self, action: GetPostmanAction):
        """
        Get postman collection
        """
        return action.execute()


@misc_ns.route('/config')
class Config(Resource):

    @inject_actions
    def get(self, action: GetConfigAction):
        """
        Get current system configuration
        """
        return action.execute()


@misc_ns.route('/healthCheck')
class Health(Resource):
    @misc_ns.marshal_with(status_fields, as_list=False)
    def get(self):
        """
        Get the health status of the application. This endpoint can be used for health check
        """
        return {'status': 'ok'}


@misc_ns.route('/version')
class Version(Resource):
    @inject_actions
    def get(self, action: GetVersionAction):
        """
        Returns information about python and plaform version of the service (including the package versions used)
        and about build of the catintel: commit SHA1, branch, build date, image and repo information.
        """
        return action.execute()
