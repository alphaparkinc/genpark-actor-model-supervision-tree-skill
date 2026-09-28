# genpark-actor-model-supervision-tree-skill

Agent Skill implementing an **Erlang/OTP-Style Actor Model & Supervision Tree** with isolated actor mailboxes, nonblocking message passing, and supervisor failure recovery.

## Architectural Overview
```mermaid
flowchart TD
    Client["Sender Client"] --> Route["ActorSystem Message Router"]
    Route --> Mailbox["Actor Mailbox Queue"]
    Mailbox --> Actor["Actor.receive(msg)"]
    Actor --> State["State Mutation"]
    Actor -. Crash .-> Sup["Supervisor: handle_failure()"]
    Sup --> Restart["One-For-One Strategy: Reset / Reinitialize State"]
```
