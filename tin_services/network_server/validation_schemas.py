from marshmallow import Schema, fields, ValidationError,validates
from marshmallow.validate import Regexp,Range


class VMIdSchema(Schema):
    vm_id = fields.Str(
        required=True, 
        validate=Regexp(r'^[a-zA-Z0-9]{3,20}$', error="Invalid VM name. Use only letters, numbers, and underscores (3-20 characters).")
    )