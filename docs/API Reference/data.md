#Data
##/data/
####GET CIAO
-------------
_params_:

- **datamap**: JSON Schema [{**timefrom**: str|bytes, **series**: [str|bytes], **timeto**: str|bytes}]
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8


##/data/{feature}/
####GET CIAO
-------------
_params_:

- **feature**: Basic text / string value
- **par**: Basic text / string value
- **timefrom**: Basic text / string value
- **timeto**: Basic text / string value
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8


##/data/{feature}/{par}
####GET CIAO
-------------
_params_:

- **el**: Basic text / string value
- **par**: Basic text / string value
- **timefrom**: Basic text / string value
- **timeto**: Basic text / string value
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8

