from mongoengine import ValidationError
from wtforms.validators import ValidationError as wtfValidationError
from flask_admin._compat import itervalues, as_unicode


def make_gridfs_args(value):
    args = {
        'id': value.grid_id,
        'coll': value.collection_name
    }

    if value.db_alias != 'default':
        args['db'] = value.db_alias

    return args


def make_thumb_args(value):
    if getattr(value, 'thumbnail', None):
        args = {
            'id': value.thumbnail._id,
            'coll': value.collection_name
        }

        if value.db_alias != 'default':
            args['db'] = value.db_alias

        return args
    else:
        return make_gridfs_args(value)


def format_error(error):
    if isinstance(error, ValidationError):
        return as_unicode(error)

    if isinstance(error, wtfValidationError):
        try:
            return '. '.join(itervalues(error.to_dict()))
        except Exception:
            resp = ''
            for v in error.to_dict().values():
                if isinstance(v, dict):
                    resp += str(v.values())
                else:
                    resp += str(v)
            return resp

    return as_unicode(error)
