from contextlib import contextmanager
from http import HTTPStatus
import logging

from apispec.ext.marshmallow.swagger import field2property, fields2jsonschema
from micro_api_ext import http_exceptions
import flask_marshmallow
from flask_restplus.model import Model as OriginalModel
from marshmallow import post_dump
import sqlalchemy
from werkzeug import cached_property

log = logging.getLogger(__name__)


class SchemaMixin(object):

    def __deepcopy__(self, memo):
        # XXX: Flask-RESTplus makes unnecessary data copying, while
        # marshmallow.Schema doesn't support deepcopyng.
        return self


class Schema(SchemaMixin, flask_marshmallow.Schema):
    pass


if flask_marshmallow.has_sqla:
    class ModelSchema(SchemaMixin, flask_marshmallow.sqla.ModelSchema):
        @post_dump
        def update_url(self, in_data):
            return in_data

    # class ModelWithImageUrlSchema(ModelSchema):
    #     # file_name = flask_marshmallow.base_fields.String(dump_to='url')


class DefaultHTTPErrorSchema(Schema):
    status = flask_marshmallow.base_fields.Integer()
    message = flask_marshmallow.base_fields.String()

    def __init__(self, http_code, **kwargs):
        super(DefaultHTTPErrorSchema, self).__init__(**kwargs)
        self.fields['status'].default = http_code


class Model(OriginalModel):

    def __init__(self, name, model, **kwargs):
        # XXX: Wrapping with __schema__ is not a very elegant solution.
        super(Model, self).__init__(name, {'__schema__': model}, **kwargs)

    @cached_property
    def __schema__(self):
        schema = self['__schema__']
        if isinstance(schema, flask_marshmallow.Schema):
            return fields2jsonschema(schema.fields)
        elif isinstance(schema, flask_marshmallow.base_fields.FieldABC):
            return field2property(schema)
        raise NotImplementedError()


@contextmanager
def execute_with_session(session, default_error_message="The operation failed to complete"):
    try:
        with session.begin():
            yield
    except ValueError as exception:
        log.info("Database transaction was rolled back due to: %r", exception)
        http_exceptions.abort(code=HTTPStatus.CONFLICT, message=str(exception))
    except sqlalchemy.exc.IntegrityError as exception:
        log.info("Database transaction was rolled back due to: %r", exception)
        http_exceptions.abort(
            code=HTTPStatus.CONFLICT,
            message=default_error_message
        )
