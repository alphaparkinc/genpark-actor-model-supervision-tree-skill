"""Erlang-Style Actor Model & Supervision Tree Engine.
100% Python Standard Library.
"""

import collections

class ActorSystem:
    """Erlang-style Actor Model with mailboxes and one-for-one supervisor restart."""
    class Actor:
        def __init__(self, name):
            self.name = name
            self.mailbox = collections.deque()
            self.state = {}

        def receive(self, message):
            pass

    def __init__(self):
        self.actors = {}
        self.supervisors = {}

    def register(self, actor, supervisor=None):
        self.actors[actor.name] = actor
        if supervisor:
            self.supervisors[actor.name] = supervisor

    def send(self, actor_name, message):
        actor = self.actors.get(actor_name)
        if not actor:
            raise ValueError(f"Actor {actor_name} not found")
        actor.mailbox.append(message)

    def process_all(self):
        dispatched = 0
        for name, actor in list(self.actors.items()):
            while actor.mailbox:
                msg = actor.mailbox.popleft()
                try:
                    actor.receive(msg)
                    dispatched += 1
                except Exception as e:
                    sup = self.supervisors.get(name)
                    if sup:
                        sup.handle_failure(actor, e)
                    else:
                        raise e
        return dispatched
