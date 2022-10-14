import json

import marshmallow as ma

class BaseSchema(ma.Schema):

    class Meta:
        render_module = json
