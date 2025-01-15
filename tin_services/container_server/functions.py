from exceptions import *
import docker
import socket



client = docker.from_env()
hostname = socket.gethostname()


# Periodic function to update vm
def sync_container(collection):
    try:
        for container in client.containers.list(all=True):
            update_item_list(container.name, "status", container.status, collection)
    except ContainerNotFound as e:
        print ({"Error updating container status": f"{e.message}"})
    except ItemNotModified as e:
        print ("Nothing to update")
        pass
    except pymongo.errors.ConnectionFailure as e:
        print ({"Error updating container status": "Connection to database failed."})
    except Exception as e:
        print ({"Error updating container status": f"Error {e}"})
    return



#Search what image to use for the given service
def search_image_by_service (service_port, collection):
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
            "$sort": {"services.priority": -1}  # Sort by priority descending
        },
        {
            "$limit": 1  # Take the top result
        }
        ]
    
    return list(collection.aggregate(pipeline))


#Search what container to use for the given service
def search_container_by_service (service_port, collection):
    pipeline = [
        {
            "$match": {
                 "$elemMatch": {
                    "service_port": f"{service_port}",
                    "busy":"False" 
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
            "$sort": {"services.priority": -1}  # Sort by priority descending
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

#Count container on vm
def count_container(containerCollection):
    pipeline = [
        {
            "$group": {
                "_id": "$vm_name",  # Group by the 'vm_name' field
                "number_of_containers": {"$sum": 1}  # Count the number of documents per vm_name
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the default '_id' field
                "vm_name": "$_id",
                "number_of_containers": 1
            }
        }
        ]
    
    return list(containerCollection.aggregate(pipeline))


def get_container_by_vm_port(vm_port, collection):

    item = collection.find_one({"vm_name": hostname , "services.vm_port":vm_port }, {"_id": 0 , "name": 1})
    print("item:",item)
    if (not item):
        print("item not found")
        raise ItemNotFound (f"Can not find container with vm_port {vm_port}.", error_code=404)
    
    #print(item)    
    return item  


