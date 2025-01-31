from marshmallow import Schema, fields, ValidationError,validates
from marshmallow.validate import Regexp,Range


class VMNameSchema(Schema):
    vm_name = fields.Str(
        required=True, 
        validate=Regexp(r'^[a-zA-Z0-9_]{3,20}$', error="Invalid VM name. Use only letters, numbers, and underscores (3-20 characters).")
    )


class VMSchema(Schema):
    vm_name = fields.Str(
        required=True,
        validate=Regexp(r'^[a-zA-Z0-9_-]{3,30}$', error="Invalid VM name. Use only letters, numbers, underscores, or hyphens (3-30 characters).")
    )

    vm_box = fields.Str(
        required=True,
        validate=Regexp(r'^[a-zA-Z0-9_-]+$', error="Invalid VM box. Use only letters, numbers, underscores, or hyphens.")
    )

    vm_cpus = fields.Int(
        required=True,
        validate=Range(min=1, max=4, error="CPU count must be between 1 and 32.")
    )

    vm_ram = fields.Int(
        required=True,
        validate=Range(min=512, max=65536, error="RAM must be between 512MB and 65536MB (64GB).")
    )

    vm_ip = fields.Str(
        required=True,
        validate=Regexp(r'^(?:\d{1,3}\.){3}\d{1,3}$', error="Invalid IP address format.")
    )

class VMUpdateSchema(Schema):

    vm_cpus = fields.Int(
        required=True,
        validate=Range(min=1, max=4, error="CPU count must be between 1 and 32.")
    )

    vm_ram = fields.Int(
        required=True,
        validate=Range(min=512, max=65536, error="RAM must be between 512MB and 65536MB (64GB).")
    )

    vm_ip = fields.Str(
        required=True,
        validate=Regexp(r'^(?:\d{1,3}\.){3}\d{1,3}$', error="Invalid IP address format.")
    )   


class ServiceSchema(Schema):
    image = fields.Str(
        required=True,
        validate=Regexp(r'^[a-zA-Z0-9/:._-]+$', error="Invalid image name. Use only letters, numbers, colons (:), slashes (/), dots (.), underscores (_), or hyphens (-).")
    )

    service_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="Service port must be between 1 and 65535.")
    )

    priority = fields.Int(
        required=True,
        validate=Range(min=1, max=10, error="Priority must be between 1 (lowest) and 10 (highest).")
    )