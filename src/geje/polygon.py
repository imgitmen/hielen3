from marshmallow.fields import (
    List,
    Str,
    Number
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    POLYGON,
)
from ._base import (
    BaseSchema,
)


class PolygonSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [POLYGON],
            error='Invalid polygon type'
        )
    )

    coordinates = List(
        List(
            List(Number(), required=True),
            required=True
        ),
        required=True,
    )
