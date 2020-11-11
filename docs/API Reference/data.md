#Data
##/data/
####GET
_params_:

- **datamap**: JSON Schema [{**series**: [str|bytes], **timefrom**: str|bytes, **timeto**: str|bytes}]
- **content_type**: Basic text / string value

_result_:

- **format**: Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)
- **content_type**: text/plain; charset=utf-8, application/json; charset=utf-8

_description_:


    if isinstance (datamap,list):
        datamap=','.join(datamap)
    try:
        loaded=json.loads(datamap)
    except json.JSONDecodeError as e:
        out = ResponseFormatter(status=falcon.HTTP_BAD_REQUEST)
        out.message=str(e)
        response = out.format(response=response,request=request)
        return
    


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


