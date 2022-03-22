from marshmallow.fields import (
    Nested,
    Str,
)
from marshmallow.validate import (
    OneOf,
)
from .object_type import (
    FEATURE,
)
from ._base import BaseSchema
from .geometry import GeometriesSchema
from .property import PropertiesSchema


class FeatureSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [FEATURE],
            error='Invalid feature type'
        )
    )

    geometry = Nested(
        GeometriesSchema,
        required=True,
    )

    properties = Nested(
        PropertiesSchema,
        required=True,
    )
