from marshmallow.fields import (
    List,
    Number,
    Str,
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    MULTI_POINT,
)
from ._base import (
    BaseSchema,
)


class MultiPointSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [MULTI_POINT],
            error='Invalid multi point type'
        )
    )

    coordinates = List(
        List(Number(), required=True),
        required=True
    )

