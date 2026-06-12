import urllib.request
import json
import socket

host = socket.gethostname()
root_pg_id = "b838654e-019e-1000-75a7-111254b943e3"
template_id = "906b4022-394f-48ed-9f07-5aa4a14fe7b7"

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

print(f"Instantiating template {template_id} into PG {root_pg_id}...")
try:
    url = f"http://{host}:8080/nifi-api/process-groups/{root_pg_id}/template-instance"
    res = post(url, {"templateId": template_id, "originX": 0, "originY": 0})
    print("✅ Template instantiated successfully")
    
    # Start all processors
    print("Starting all processors...")
    url_start = f"http://{host}:8080/nifi-api/flow/process-groups/{root_pg_id}"
    res_start = post(url_start, {"id": root_pg_id, "state": "RUNNING"})
    print("✅ All processors started")

except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
