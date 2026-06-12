import urllib.request
import json
import socket

host = socket.gethostname()
root_pg_id = "b838654e-019e-1000-75a7-111254b943e3"

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def create_processor(pg_id, name, type, x, y, config={}):
    url = f"http://{host}:8080/nifi-api/process-groups/{pg_id}/processors"
    data = {
        "revision": {"version": 0},
        "component": {
            "name": name,
            "type": type,
            "position": {"x": x, "y": y},
            "config": config
        }
    }
    return post(url, data)

def create_connection(pg_id, source_id, target_id, relationships):
    url = f"http://{host}:8080/nifi-api/process-groups/{pg_id}/connections"
    data = {
        "revision": {"version": 0},
        "component": {
            "source": {"id": source_id, "type": "PROCESSOR"},
            "destination": {"id": target_id, "type": "PROCESSOR"},
            "selectedRelationships": relationships
        }
    }
    return post(url, data)

try:
    print("Creating ListenHTTP...")
    listen = create_processor(root_pg_id, "ListenHTTP", "org.apache.nifi.processors.standard.ListenHTTP", 0, 0, {
        "properties": {"Listening Port": "8888"}
    })
    
    print("Creating JoltTransformJSON...")
    jolt = create_processor(root_pg_id, "JoltTransformJSON", "org.apache.nifi.processors.standard.JoltTransformJSON", 400, 0)
    
    print("Creating ExecuteStreamCommand...")
    exec_cmd = create_processor(root_pg_id, "WriteToBigtable", "org.apache.nifi.processors.standard.ExecuteStreamCommand", 800, 0, {
        "properties": {
            "Command Path": "python3",
            "Command Arguments": "/opt/nifi/nifi-current/conf/write_to_bigtable.py",
            "Argument Strategy": "Command Arguments Property"
        }
    })
    
    print("Connecting processors...")
    create_connection(root_pg_id, listen["id"], jolt["id"], ["success"])
    create_connection(root_pg_id, jolt["id"], exec_cmd["id"], ["success"])
    
    print("Starting all processors...")
    post(f"http://{host}:8080/nifi-api/flow/process-groups/{root_pg_id}", {"id": root_pg_id, "state": "RUNNING"})
    
    print("✅ NiFi Flow created and started successfully")

except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
