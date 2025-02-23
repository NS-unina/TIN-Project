from marshmallow import Schema, fields, ValidationError,validates
from marshmallow.validate import Regexp,Range



class ContainerSchema(Schema):
    name = fields.Str(
        required=False,
        validate=Regexp(
            r'$|^[a-zA-Z0-9][a-zA-Z0-9_.-]{2,62}$',
            error="Invalid container name. Must be 3-63 characters long, start with a letter or number, and contain only letters, numbers, dots (.), underscores (_), or hyphens (-)."
        )
    )

    service_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="Service port must be between 1 and 65535.")
    )

    @validates("name")
    def validate_container_name(self, value):
        """Ensure container name does not contain consecutive dots or dashes."""
        if ".." in value or "--" in value:
            raise ValidationError("Container name cannot contain consecutive dots (..) or hyphens (--).")
        if value.startswith(".") or value.startswith("-"):
            raise ValidationError("Container name cannot start with a dot (.) or hyphen (-).")
        

class ContainerNameSchema(Schema):
    container_name = fields.Str(
        required=True,
        validate=Regexp(
            r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{2,62}$',
            error="Invalid container name. Must be 3-63 characters long, start with a letter or number, and contain only letters, numbers, dots (.), underscores (_), or hyphens (-)."
        )
    )

    @validates("container_name")
    def validate_container_name(self, value):
        """Ensure container name does not contain consecutive dots or dashes."""
        if ".." in value or "--" in value:
            raise ValidationError("Container name cannot contain consecutive dots (..) or hyphens (--).")
        if value.startswith(".") or value.startswith("-"):
            raise ValidationError("Container name cannot start with a dot (.) or hyphen (-).")


    
class VMPortSchema(Schema):
    vm_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="VM port must be between 1 and 65535.")
    )

class ServicePortSchema(Schema):
    service_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="Service port must be between 1 and 65535.")
    )


def validate_busy(value):
    if value not in ["True", "False"]:
        raise ValidationError("Busy must be equal to 'True' or 'False'.")

class UpdateSchema(Schema):
    busy = fields.String(required=True, validate=validate_busy)

