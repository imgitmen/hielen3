##prototypes

		/prototypes/
#####POST
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'code': {'type': 'Basic text / string value'}}}_
#####GET
_{'examples': ['http://localhost/prototypes/?/'], 'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}}_

		/prototypes/{eltype}
#####GET
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'eltype': {'type': 'Basic text / string value'}}}_

		/prototypes/{eltype}/forms
#####GET
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'eltype': {'type': 'Basic text / string value'}}}_

		/prototypes/{eltype}/forms/{form}
#####GET
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'eltype': {'type': 'Basic text / string value'}, 'form': {'type': 'Basic text / string value'}}}_
##elements

		/elements/
#####POST
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'code': {'type': 'Basic text / string value'}, 'prototype': {'type': 'Basic text / string value'}}}_
#####GET
_{'examples': ['http://localhost/elements/'], 'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'elist': {'type': 'Basic text / string value'}}}_

		/elements/{code}
#####GET
_{'outputs': {'format': 'JSON (Javascript Serialized Object Notation)', 'content_type': 'application/json; charset=utf-8'}, 'inputs': {'code': {'type': 'Basic text / string value'}}}_
##series

		/series/
#####GET
_{'outputs': {'format': 'Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)', 'content_type': 'text/plain; charset=utf-8, application/json; charset=utf-8'}, 'inputs': {'datamap': {'type': 'Basic text / string value'}}}_

		/series/{el}/
#####GET
_{'outputs': {'format': 'Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)', 'content_type': 'text/plain; charset=utf-8, application/json; charset=utf-8'}, 'inputs': {'el': {'type': 'Basic text / string value'}, 'par': {'type': 'Basic text / string value'}, 'timefrom': {'type': 'Basic text / string value'}, 'timeto': {'type': 'Basic text / string value'}}}_

		/series/{el}/{par}
#####GET
_{'examples': ['http://localhost/series/{el}/{par}'], 'outputs': {'format': 'Supports any of the following formats: Free form UTF-8 text, JSON (Javascript Serialized Object Notation)', 'content_type': 'text/plain; charset=utf-8, application/json; charset=utf-8'}, 'inputs': {'el': {'type': 'Basic text / string value'}, 'par': {'type': 'Basic text / string value'}, 'timefrom': {'type': 'Basic text / string value'}, 'timeto': {'type': 'Basic text / string value'}}}_
