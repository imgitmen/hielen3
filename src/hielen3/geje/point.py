from marshmallow.fields import (
    List,
    Str,
    Number
)

from marshmallow.validate import (
    OneOf,
)

from .object_type import (
    POINT,
)

from ._base import (
        BaseSchema,
        )

class PointSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [POINT],
            error='Invalid point type'
        )
    )

    coordinates = List(
        Number(),
        required=True
    )
