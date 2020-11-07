import asyncio
import websockets
import json
import logging

logging.basicConfig()

connected_clients_set = set()
global_history_message_list = list()
messages_to_send = ''


def users_event():
    return json.dumps({"type": "users", "count": len(connected_clients_set)})


def state_event():
    return json.dumps({"type": "message", "messages": messages_to_send})


async def notify_state():
    if connected_clients_set:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in connected_clients_set])


async def notify_users():
    if connected_clients_set:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in connected_clients_set])


async def register(websocket):
    connected_clients_set.add(websocket)
    await notify_users()


async def unregister(websocket):
    connected_clients_set.remove(websocket)
    await notify_users()


async def server_start(websocket, path):
    global messages_to_send
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            if message["type"] == "message":
                message_dict = json.loads(message)
                messages_to_send = message_dict['messages']
                await notify_state()
            else:
                logging.error("unsupported event: {}", message)
    finally:
        await unregister(websocket)

# async def server_start(websocket, path):
#     while True:
#         msg = await websocket.recv()
#         print(f'[Received]: {msg}')
#         msg = f"{msg}"
#         await websocket.send(msg)
#         msg2 = "This is an automated response."
#         await websocket.send("Server: This is an automated response.")
#         print(f'[Sent]: {msg}')
#         print(f'[Sent]: {msg2}')


if __name__ == "__main__":
    start_server = websockets.serve(server_start, "localhost", 5502)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
