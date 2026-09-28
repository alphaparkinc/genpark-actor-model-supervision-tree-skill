import sys
import json
from client import ActorSystem

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-actor-model-supervision-tree-skill", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "dispatch_actor_messages",
                        "description": "Send and process messages across actors with supervision restart handling",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "actor_name": {"type": "string", "default": "worker"},
                                "messages": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["messages"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "dispatch_actor_messages":
            system = ActorSystem()
            name = args.get("actor_name", "worker")
            class TestActor(system.Actor):
                def receive(self, msg):
                    if msg == "crash":
                        raise RuntimeError("Crash directive")
                    self.state["history"] = self.state.get("history", []) + [msg]
            class Sup:
                def __init__(self):
                    self.restarts = 0
                def handle_failure(self, actor, exc):
                    self.restarts += 1
                    actor.state = {"history": ["restarted"]}
            actor = TestActor(name)
            sup = Sup()
            system.register(actor, supervisor=sup)
            for m in args.get("messages", []):
                system.send(name, m)
            dispatched = system.process_all()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"final_state": actor.state, "restarts": sup.restarts, "dispatched": dispatched})}]
                }
            }
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
