import asyncio
import websockets
import json
from game_logic import Game

game = Game()


async def handle_client(websocket, path):
    print(f"New client connected: {path}")

    player = path.strip('/')
    if player not in ['A', 'B']:
        await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid player'}))
        return

    while True:
        try:
            message = await websocket.recv()
            print(f"Received message: {message}")  # Debugging output

            data = json.loads(message)

            if data['type'] == 'deploy':
                positions = data['data']
                if game.deploy_characters(player, positions):
                    response = {'type': 'state_update', 'data': game.get_game_state()}
                    await websocket.send(json.dumps(response))
                else:
                    await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid deployment'}))

            elif data['type'] == 'move':
                result = game.process_move(player, data['data']['character'], data['data']['move'])
                if result == 'Move successful':
                    response = {'type': 'state_update', 'data': game.get_game_state()}
                    await websocket.send(json.dumps(response))
                else:
                    await websocket.send(json.dumps({'type': 'error', 'message': result}))

                if game.is_game_over():
                    await websocket.send(json.dumps({'type': 'response', 'message': 'Game over'}))
                    break

        except websockets.ConnectionClosed:
            print("Connection closed")
            break
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({'type': 'error', 'message': str(e)}))


async def main():
    print("Starting server...")
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server is running")
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
    print("Running")
