from marshmallow import Schema, fields, ValidationError,validates,pre_load
from marshmallow.validate import Regexp,Range


class VMNameSchema(Schema):
    vm_name = fields.Str(
        required=True, 
        validate=Regexp(r'$|^[a-zA-Z0-9-]{3,20}$', error="Invalid VM name. Use only letters, numbers,  (3-20 characters).")
    )


class VMSchema(Schema):
    name = fields.Str(
        required=False,
        validate=Regexp(r'$|^[a-zA-Z0-9-]{3,30}$', error="Invalid VM name. Use only letters, numbers, or hyphens (3-30 characters).")
    )

    box = fields.Str(
        required=False,
        validate=Regexp(r'$|^[a-zA-Z0-9-\/]+$', error="Invalid VM box. Use only letters, numbers, slash, or hyphens.")
    )

    cpus = fields.Str(
        required=False,
        validate=Regexp(r'$|^[1-4]$', error="Invalid CPU count must be between 1 and 4.")
    )    
    
    ram = fields.Str(
        required=False,
        validate=Regexp(r'$|^(512|[5-9]\d{2}|[1-5]\d{3}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-6])$', error="Invalid RAM count must be between 512MB and 65536MB (64GB).")
    )
   
    ip = fields.Str(
        required=False,
        validate=Regexp(r'$|^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', error="Invalid IP address format.")
        
    )


class VMUpdateSchema(Schema):

    cpus = fields.Str(
        required=False,
        validate=Regexp(r'$|^[1-4]$', error="Invalid CPU count must be between 1 and 4.")
    )  

    ram = fields.Str(
        required=False,
        validate=Regexp(r'$|^(512|[5-9]\d{2}|[1-5]\d{3}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-6])$', error="Invalid RAM count must be between 512MB and 65536MB (64GB).")
    )

    ip = fields.Str(
        required=False,
        validate=Regexp(r'$|^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', error="Invalid IP address format.")
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