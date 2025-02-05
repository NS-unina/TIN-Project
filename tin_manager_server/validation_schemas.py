from marshmallow import Schema, fields, ValidationError,validates
from marshmallow.validate import Regexp,Range



class AddFlowSchema(Schema):


    src_ip = fields.Str(
        required=False,
        validate=Regexp(r'$|^(?:\d{1,3}\.){3}\d{1,3}$', error="Invalid IP address format.")
    ) 
    dst_ip = fields.Str(
        required=False,
        validate=Regexp(r'$|^(?:\d{1,3}\.){3}\d{1,3}$', error="Invalid IP address format.")
    )

    src_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="Source port must be between 1 and 65535.")
    )

    dst_port = fields.Int(
        required=True,
        validate=Range(min=1, max=65535, error="Destination port must be between 1 and 65535.")
    )

    ovs_id = fields.Str(
        required=True, 
        validate=Regexp(r'^[a-zA-Z0-9:]{3,20}$', error="Invalid OVS id. Use only letters, numbers, and (:)  (3-20 characters).")
    )
  
class MAX_CONTAINERSchema(Schema):
     max_containers = fields.Int(
        required=True,
        validate=Range(min=1, max=30, error="Max containers must be between 1 and 30.")
    )
