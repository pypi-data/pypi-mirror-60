from flask import request
from flask_restplus import Resource, fields, Namespace
from micropydd.actions import GetLoggersAction, SetLoggerAction, GetLoggerAction

from micropydd_restplus.decorators import inject_actions

loggers_ns = Namespace('loggers', description='Manage logger')

logger_fields = loggers_ns.model('Logger', {
    'name': fields.String(required=True),
    'level': fields.String(required=True, enum=['INFO', 'DEBUG', 'ERROR', 'WARN']),
})


@loggers_ns.route('/')
class LoggersResource(Resource):
    """
    Get loggers
    """

    @loggers_ns.marshal_with(logger_fields, as_list=True, )
    @loggers_ns.response(200, 'Success')
    @inject_actions
    def get(self, action: GetLoggersAction):
        """
        Get All loggers information
        """
        return action.execute()

    @loggers_ns.expect(logger_fields, validate=True)
    @loggers_ns.marshal_with(logger_fields, as_list=False)
    @loggers_ns.response(200, 'Success')
    @loggers_ns.response(400, 'Validation Error')
    @inject_actions
    def post(self, action: SetLoggerAction):
        """
        Set loggers information
        """
        data = request.json
        return action.execute(data.get("name"), data.get("level"))


@loggers_ns.route('/<name>')
class LoggerResource(Resource):

    @loggers_ns.marshal_with(logger_fields, as_list=False)
    @loggers_ns.response(200, 'Success')
    @inject_actions
    def get(self, action: GetLoggerAction, name: str):
        """
        Get specific logger information
        """
        logger = action.execute(name)
        return logger
