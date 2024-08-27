import asyncio  # Import asyncio for asynchronous operations
import websockets  # Import websockets for handling WebSocket connections
import json  # Import json for handling JSON data
from game_logic import Game  # Import the Game class from game_logic module

# Create an instance of the Game class
game = Game()

async def handle_client(websocket, path):
    # Function to handle communication with a single client
    print(f"New client connected: {path}")

    player = path.strip('/')  # Extract player identifier (either 'A' or 'B') from the path
    if player not in ['A', 'B']:
        # If the player identifier is invalid, send an error message and return
        await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid player'}))
        return

    while True:
        try:
            # Receive a message from the client
            message = await websocket.recv()
            print(f"Received message: {message}")  # Debugging output

            # Parse the received message
            data = json.loads(message)

            if data['type'] == 'deploy':
                # Handle deployment of characters
                positions = data['data']
                if game.deploy_characters(player, positions):
                    # If deployment is successful, send the updated game state
                    response = {'type': 'state_update', 'data': game.get_game_state()}
                    await websocket.send(json.dumps(response))
                else:
                    # If deployment fails, send an error message
                    await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid deployment'}))

            elif data['type'] == 'move':
                # Handle movement of characters
                result = game.process_move(player, data['data']['character'], data['data']['move'])
                if result == 'Move successful':
                    # If move is successful, send the updated game state
                    response = {'type': 'state_update', 'data': game.get_game_state()}
                    await websocket.send(json.dumps(response))
                else:
                    # If move fails, send an error message
                    await websocket.send(json.dumps({'type': 'error', 'message': result}))

                # Check if the game is over and send a game over message if true
                if game.is_game_over():
                    await websocket.send(json.dumps({'type': 'response', 'message': 'Game over'}))
                    break  # Exit the loop if the game is over

        except websockets.ConnectionClosed:
            # Handle the case when the WebSocket connection is closed
            print("Connection closed")
            break
        except Exception as e:
            # Handle any other exceptions
            print(f"Error: {e}")
            await websocket.send(json.dumps({'type': 'error', 'message': str(e)}))

async def main():
    # Main function to start the WebSocket server
    print("Starting server...")
    async with websockets.serve(handle_client, "localhost", 8765):
        # Start the WebSocket server on localhost at port 8765
        print("Server is running")
        await asyncio.Event().wait()  # Keep the server running

if __name__ == "__main__":
    # Entry point of the script
    asyncio.run(main())  # Run the main function
    print("Running")  # This line will not be reached due to asyncio.run()
