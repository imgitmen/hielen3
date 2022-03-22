from marshmallow.fields import (
    List,
    Number,
    Str,
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    MULTI_POLYGON,
)
from ._base import (
    BaseSchema,
)


class MultiPolygonSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [MULTI_POLYGON],
            error='Invalid multi polygon type'
        )
    )

    coordinates = List(
        List(
            List(
                List(Number(), required=True),
                required=True
            ),
            required=True,
        ),
        required=True,
    )

