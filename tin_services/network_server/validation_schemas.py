from marshmallow import Schema, fields, ValidationError,validates
from marshmallow.validate import Regexp,Range


class VMIdSchema(Schema):
    vm_id = fields.Str(
        required=True, 
        validate=Regexp(r'^[a-zA-Z0-9]{3,5}$', error="Invalid VM id. Use only letters, numbers (3-5 characters).")
    )