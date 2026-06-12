import urllib.request
import json
import socket

host = socket.gethostname()
root_id = "b838654e-019e-1000-75a7-111254b943e3"

def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())

def put(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='PUT')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

# 1. Fix JoltTransformJSON
print("Fixing JoltTransformJSON...")
jolt_id = "b8462d60-019e-1000-54dd-2f8f01e4c5dd"
jolt = get(f"http://{host}:8080/nifi-api/processors/{jolt_id}")
put(f"http://{host}:8080/nifi-api/processors/{jolt_id}", {
    "revision": jolt["revision"],
    "component": {
        "id": jolt_id,
        "config": {
            "properties": {
                "jolt-transform": "jolt-transform-sort",
                "jolt-spec": None
            },
            "autoTerminatedRelationships": ["failure"]
        }
    }
})


# 2. Fix WriteToBigtable
print("Fixing WriteToBigtable...")
exec_id = "b8462d86-019e-1000-ecdd-166d641afdfe"
exec_p = get(f"http://{host}:8080/nifi-api/processors/{exec_id}")
put(f"http://{host}:8080/nifi-api/processors/{exec_id}", {
    "revision": exec_p["revision"],
    "component": {
        "id": exec_id,
        "config": {
            "autoTerminatedRelationships": ["original", "output stream", "nonzero status"]
        }
    }
})

# 3. Start Root
print("Starting flow...")
root = get(f"http://{host}:8080/nifi-api/process-groups/{root_id}")
put(f"http://{host}:8080/nifi-api/flow/process-groups/{root_id}", {"id": root_id, "state": "RUNNING"})

print("✅ Fixes applied and flow started")
