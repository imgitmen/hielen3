from marshmallow.fields import (
    List,
    Str,
    Number
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    LINE_STRING,
)
from ._base import (
    BaseSchema,
)


class LineStringSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [LINE_STRING],
            error='Invalid line string type'
        )
    )

    coordinates = List(
        List(Number(), required=True),
        required=True,
    )
