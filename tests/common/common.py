import json
from couchbase.management.collections import CollectionManager

# Function to create scope if it doesn't exist
def create_scope_if_not_exists(collection_manager,scope_name):
    scopes = collection_manager.get_all_scopes()
    scope_names = [scope.name for scope in scopes]
    
    if scope_name not in scope_names:
        collection_manager.create_scope(scope_name)
        #print(f"Scope '{scope_name}' created.")

# Function to create collection if it doesn't exist
def create_collection_if_not_exists(collection_manager :CollectionManager, scope_name, collection_name):
    scopes = collection_manager.get_all_scopes()
    
    for scope in scopes:
        if scope.name == scope_name:
            collection_names = [collection.name for collection in scope.collections]
            
            if collection_name not in collection_names:
                collection_manager.create_collection(scope_name=scope_name,collection_name=collection_name)
                #print(f"Collection '{collection_name}' in scope '{scope_name}' created.")
            return
    
    #print(f"Scope '{scope_name}' does not exist, cannot create collection '{collection_name}'.")


def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)