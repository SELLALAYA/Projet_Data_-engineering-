import urllib.request
import json
import socket
import time

host = socket.gethostname()

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())

def delete(url, version):
    req = urllib.request.Request(f"{url}?version={version}", method='DELETE')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

# 1. Get Root PG ID
root_pg = get(f"http://{host}:8080/nifi-api/process-groups/root")
root_id = root_pg["id"]
print(f"Root PG: {root_id}")

# 2. Delete all existing processors
procs = get(f"http://{host}:8080/nifi-api/process-groups/{root_id}/processors")
for p in procs["processors"]:
    print(f"Deleting processor {p['component']['name']}...")
    delete(f"http://{host}:8080/nifi-api/processors/{p['id']}", p["revision"]["version"])

# 3. Create processors
def create_proc(name, type, x, y, props={}):
    print(f"Creating {name}...")
    return post(f"http://{host}:8080/nifi-api/process-groups/{root_id}/processors", {
        "revision": {"version": 0},
        "component": {
            "name": name,
            "type": type,
            "position": {"x": x, "y": y},
            "config": {"properties": props}
        }
    })

listen = create_proc("ListenHTTP", "org.apache.nifi.processors.standard.ListenHTTP", 0, 0, {"Listening Port": "8888"})
jolt = create_proc("JoltTransformJSON", "org.apache.nifi.processors.standard.JoltTransformJSON", 400, 0)
exec_cmd = create_proc("WriteToBigtable", "org.apache.nifi.processors.standard.ExecuteStreamCommand", 800, 0, {
    "Command Path": "python3",
    "Command Arguments": "/opt/nifi/nifi-current/conf/write_to_bigtable.py",
    "Argument Strategy": "Command Arguments Property"
})

# 4. Create connections
def connect(src_id, dest_id, rels):
    print(f"Connecting {src_id} to {dest_id}...")
    return post(f"http://{host}:8080/nifi-api/process-groups/{root_id}/connections", {
        "revision": {"version": 0},
        "component": {
            "source": {"id": src_id, "type": "PROCESSOR"},
            "destination": {"id": dest_id, "type": "PROCESSOR"},
            "selectedRelationships": rels
        }
    })

connect(listen["id"], jolt["id"], ["success"])
connect(jolt["id"], exec_cmd["id"], ["success"])

# 5. Start
print("Starting flow...")
post(f"http://{host}:8080/nifi-api/flow/process-groups/{root_id}", {"id": root_id, "state": "RUNNING"})

print("✅ Setup complete")
