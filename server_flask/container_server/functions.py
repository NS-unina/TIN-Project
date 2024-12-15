from exceptions import *
import docker
import json
import socket



client = docker.from_env()
hostname = socket.gethostname()


#Search what image to use for the given service
def search_services (service_port, collection):
    pipeline = [
        {
            "$match": {
                "services": {
                    "$elemMatch": {"service_port": f"{service_port}"}
                }
            }
        },
        {
            "$unwind": "$services"
        },
        {
            "$match": {
                "services.service_port": f"{service_port}"
            }
        },
        {
            "$sort": {"services.priority": 1}  # Sort by priority descending
        },
        {
            "$limit": 1  # Take the top result
        }
        ]
    
    return list(collection.aggregate(pipeline))


#Create item in the list
def create_item_list(container, all_services, containerCollection):

    new_container={
        "name": container.name,
        "image": str(container.image),
        "status": container.status,
        "vm_name": hostname,
        "services": all_services["services"]
    }

    result = containerCollection.insert_one(new_container)
    if (not result):
        raise FailedInsertion(f"Insert of container {container.name} failed", error_code=500)

    new_container.pop("_id", None)
    return new_container 


#Search if value exists
def check_if_value_field_exists(field, value, collection):

    item = collection.find_one({"vm_name": hostname , field:value }, {"_id": 0 })
    if (not item):
        return False
    return True


#Delete from db
def delete_from_db(container_name,containerCollection):

    result = containerCollection.delete_one({"name": container_name})
    if (result.deleted_count==0):
        raise ItemNotFound (f"Cannot delete vm {container_name} ", error_code=400) 


#Update field in list
def update_item_list(container_name, field, value_field, collection):

    result = collection.update_one(
        {"vm_name": hostname, "name": container_name},            
        {"$set": {field: value_field}}
        )
    
    if (result.matched_count==0):
        raise ContainerNotFound (f"Can not find container '{container_name}'.", error_code=404)
    if(result.modified_count==0):
        raise ItemNotModified (f"Field '{field}' not modified.", error_code=200)
