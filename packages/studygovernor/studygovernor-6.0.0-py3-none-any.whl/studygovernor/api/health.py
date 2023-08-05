from flask import Blueprint
from flask_restplus import Api, Resource
from sqlalchemy.exc import SQLAlchemyError


blueprint = Blueprint('health_api', __name__)

api = Api(
    blueprint,
    version='1.0',
    title='Study Governor health REST API',
    description='The Study Governor is for tracking experiments and study resources.',
    default_mediatype='application/json'
)


@api.route('/healthy')
class Healthy(Resource):
    @api.doc('Endpoint to check if flask app is running')
    @api.response(200, 'Healthy')
    def get(self):
        return


@api.route('/ready')
class Ready(Resource):
    @api.doc('Endpoint to check if flask app ready (e.g. all resources are available and functioning)')
    @api.response(200, 'Ready')
    @api.response(500, 'Not ready')
    def get(self):
        try:
            from studygovernor import models
            models.db.session.query(models.Scantype).first()
            return None
        except SQLAlchemyError:
            return None, 500
