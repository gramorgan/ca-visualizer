import aiohttp
from aiohttp import web
from ca_world import gen_ca

async def handle_index(request):
    return web.FileResponse('./static/index.html')

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print('websocket connection opened')

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
                continue
            payload = msg.json()
            if payload['type'] == 'start_ca':
                n = payload['n']
                p = payload['p']
                q = payload['q']
                # reset graph and set new params
                await ws.send_json({
                    'type': 'setup',
                    'n': n,
                })
                # send each frame as they're generated
                async for frame in gen_ca(n, p, q):
                    await ws.send_json({
                        'type': 'data',
                        'value': frame,
                    })
                await ws.send_json({
                    'type': 'finish',
                })
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                ws.exception())

    print('websocket connection closed')

    return ws

app = web.Application()
app.router.add_static('/static', './static')
app.add_routes([
    web.get('/', handle_index),
    web.get('/socket', handle_websocket),
])

if __name__ == '__main__':
    web.run_app(app)