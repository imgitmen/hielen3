#Data
##/data/
####GET
_params_:

- **datamap**: schema:
{
    series: list of str, bytes
    timefrom: str, bytes, required
    timeto: datetime.datetime

}
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


