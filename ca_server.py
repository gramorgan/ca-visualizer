import aiohttp
from aiohttp import web
import ca_eco
from multiprocessing import Process, Pipe
import asyncio
import concurrent.futures

async def handle_index(request):
    return web.FileResponse('./static/index.html')

async def poll_results(pipe, ws):
    while True:
        if not pipe.poll():
            await asyncio.sleep(0.1)
            continue
        frame = pipe.recv()
        if frame is None:
            await ws.send_json({
                'type': 'finish',
            })
            return
        else:
            await ws.send_json({
                'type': 'data',
                'value': frame,
            })

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print('websocket connection opened')

    poll_task = None
    pipe = None

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                if pipe:
                    pipe.send(None)
                    await poll_task
                await ws.close()
                continue
            payload = msg.json()
            if payload['type'] == 'start':
                if poll_task and not poll_task.done():
                    pipe.send(None)
                    await poll_task

                n = payload['n']
                p = payload['p']
                q = payload['q']
                # reset graph and set new params
                await ws.send_json({
                    'type': 'setup',
                    'n': n,
                })

                conn1, conn2 = Pipe(True)
                pipe = conn1
                Process(target=ca_eco.gen_ca, args=(n, p, q, conn2)).start()
                poll_task = asyncio.create_task(poll_results(pipe, ws))

            elif payload['type'] == 'stop':
                if pipe:
                    pipe.send(None)
                    await poll_task

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