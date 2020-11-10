#Data
##/data/
####GET
_params_:

- **datamap**: {'declared_fields': {'timefrom': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'timeto': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'series': <fields.List(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid list.'})>}, 'many': False, 'only': None, 'exclude': set(), 'ordered': False, 'load_only': set(), 'dump_only': set(), 'partial': False, 'unknown': 'raise', 'context': {}, 'fields': {'timeto': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'timefrom': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'series': <fields.List(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid list.'})>}, 'load_fields': {'timeto': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'timefrom': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'series': <fields.List(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid list.'})>}, 'dump_fields': {'timeto': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'timefrom': <fields.String(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid string.', 'invalid_utf8': 'Not a valid utf-8 string.'})>, 'series': <fields.List(default=<marshmallow.missing>, attribute=None, validate=None, required=False, load_only=False, dump_only=False, missing=<marshmallow.missing>, allow_none=False, error_messages={'required': 'Missing data for required field.', 'null': 'Field may not be null.', 'validator_failed': 'Invalid value.', 'invalid': 'Not a valid list.'})>}, 'error_messages': {'type': 'Invalid input type.', 'unknown': 'Unknown field.'}}
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8


##/data/{el}/
####GET
_params_:

- **el**: Basic text / string value
- **par**: Basic text / string value
- **timefrom**: Basic text / string value
- **timeto**: Basic text / string value
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8


##/data/{el}/{par}
####GET
_params_:

- **el**: Basic text / string value
- **par**: Basic text / string value
- **timefrom**: Basic text / string value
- **timeto**: Basic text / string value
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8


