from marshmallow.fields import (
    List,
    Number,
    Str,
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    MULTI_LINE_STRING,
)
from ._base import (
    BaseSchema,
)


class MultiLineStringSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [MULTI_LINE_STRING],
            error='Invalid multi line string string type'
        )
    )

    coordinates = List(
        List(
            List(Number(), required=True),
            required=True
        ),
        required=True,
    )

