from client import ActorSystem

system = ActorSystem()

class WorkerActor(system.Actor):
    def receive(self, msg):
        if msg == "error":
            raise ValueError("Simulated fault")
        self.state["items"] = self.state.get("items", 0) + 1

class SimpleSupervisor:
    def __init__(self):
        self.restarts = 0
    def handle_failure(self, actor, exc):
        self.restarts += 1
        actor.state = {"items": 0}

worker = WorkerActor("worker1")
sup = SimpleSupervisor()
system.register(worker, supervisor=sup)

system.send("worker1", "job1")
system.send("worker1", "error")
system.send("worker1", "job2")
system.process_all()

print(f"Worker State: {worker.state}, Restarts: {sup.restarts}")
