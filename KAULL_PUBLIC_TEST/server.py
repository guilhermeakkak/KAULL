import json, os, secrets
from aiohttp import web

ROOT = os.path.dirname(os.path.abspath(__file__))
rooms = {}
MAX_FREE = 3

async def index(request):
    return web.FileResponse(os.path.join(ROOT, "index.html"))

async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    room = pid = None
    try:
        async for msg in ws:
            if msg.type != web.WSMsgType.TEXT:
                continue
            try:
                data = json.loads(msg.data)
            except Exception:
                continue
            typ = data.get("type")

            if typ == "create":
                room = secrets.token_urlsafe(7).replace("-", "").replace("_", "")[:10]
                name = str(data.get("name") or "Amigo")[:32]
                pid = secrets.token_hex(6)
                rooms[room] = {"peers": {pid: {"ws": ws, "name": name}}, "plan": "free"}
                await ws.send_json({"type":"created","room":room,"id":pid,"peers":[],"max":MAX_FREE})

            elif typ == "join":
                room = str(data.get("room") or "").strip()[:32]
                name = str(data.get("name") or "Amigo")[:32]
                r = rooms.get(room)
                if not r:
                    await ws.send_json({"type":"error","message":"Essa sala não existe ou já foi encerrada."})
                    continue
                if len(r["peers"]) >= MAX_FREE:
                    await ws.send_json({"type":"error","message":"Sala Free cheia (máximo de 3 pessoas)."})
                    continue
                pid = secrets.token_hex(6)
                existing = [{"id":k,"name":v["name"]} for k,v in r["peers"].items()]
                r["peers"][pid] = {"ws":ws,"name":name}
                await ws.send_json({"type":"joined","room":room,"id":pid,"peers":existing,"max":MAX_FREE})
                for k,v in list(r["peers"].items()):
                    if k != pid:
                        await v["ws"].send_json({"type":"peer-joined","id":pid,"name":name})

            elif typ == "signal" and room and pid:
                target = data.get("target")
                p = rooms.get(room,{}).get("peers",{}).get(target)
                if p:
                    await p["ws"].send_json({"type":"signal","from":pid,"data":data.get("data")})
    finally:
        if room and pid and room in rooms:
            r = rooms[room]
            r["peers"].pop(pid, None)
            for v in list(r["peers"].values()):
                try: await v["ws"].send_json({"type":"peer-left","id":pid})
                except Exception: pass
            if not r["peers"]:
                rooms.pop(room, None)
    return ws

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", ws_handler)

async def health(request):
    return web.json_response({"ok": True, "service": "KAULL", "rooms": len(rooms)})

app.router.add_get("/health", health)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"KAULL ONLINE na porta {port}")
    web.run_app(app, host="0.0.0.0", port=port)
