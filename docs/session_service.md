# AI-DnD Session Service

The session service delivers the minimum viable product for driving the
Chronomancer console against a live-ish backend. It exposes deterministic
showcase turns over a simple API so designers can practice the workflow that the
full Dungeon Master integration will eventually power.

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/sessions` | Create a new deterministic session. Accepts `mode`, `turns`, and `seed` parameters (only `mode="demo"` is supported in the MVP). |
| `GET` | `/sessions/{id}` | Retrieve the current state for a session including every frame revealed so far. |
| `POST` | `/sessions/{id}/advance` | Reveal additional turns. Accepts an optional `steps` payload (default `1`). |
| `GET` | `/sessions` | List session ids currently tracked in memory. |

Each response returns the quest hook, all frames that have been exposed, the
current pointer, and the conclusion once the final frame has been surfaced.

## Architecture

- **Showcase simulator** – Reuses `examples.simple_demo.showcase_engine` to
  produce deterministic frames with the same schema as the offline demos.
- **Session manager** – Stores `LiveSession` instances in memory, handles thread
  safety, and enforces pointer advancement.
- **FastAPI app** – Provides the HTTP layer, CORS configuration, and validation
  via Pydantic models.

The service intentionally keeps state in memory so it can be restarted quickly
without a database. Later iterations can swap in a persistent backend and the
real Dungeon Master call chain without changing the client contract.

## Running locally

```bash
pip install -r requirements.txt
python -m session_service --host 127.0.0.1 --port 8001
```

With the service running, launch the Chronomancer console (see
`examples/web_frontend/README.md`), adjust the **Session service** field if you
need a non-default host, and click **Start live session**. The console will call
`/sessions`, reveal turns via `/advance`, and update the timeline, roster, and
dossier each time a new frame arrives.

Pass `?service=http://host:port` in the console URL if you expose the API on a
non-default address. Alternatively, run `make mvp-session` from the project root
to start the service with the default host/port.
