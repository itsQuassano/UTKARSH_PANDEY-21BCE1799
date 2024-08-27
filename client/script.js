// Event listener for when the DOM content is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const boardSize = 5; // Size of the game board (5x5 grid)
    const boardElement = document.getElementById('game-board'); // Game board element
    const statusElement = document.getElementById('status'); // Status display element
    const moveHistoryList = document.getElementById('move-history-list'); // Move history list element

    // Create a WebSocket connection to the server
    const ws = new WebSocket('ws://localhost:8765/A');  // Connect as player A

    let gameState = []; // Array to hold the state of the game board
    let selectedPiece = null; // Currently selected piece
    let moveHistory = []; // Array to keep track of move history

    // Event handler for when the WebSocket connection is established
    ws.onopen = function() {
        console.log('WebSocket connection established');
        initializeBoard(); // Initialize the game board
    };

    // Event handler for WebSocket errors
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    // Event handler for when the WebSocket connection is closed
    ws.onclose = function(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
    };

    // Event handler for receiving messages from the WebSocket server
    ws.onmessage = function(event) {
        console.log('Received message:', event.data);
        const message = JSON.parse(event.data); // Parse the received message
        if (message.type === 'state_update') {
            gameState = message.data; // Update the game state
            updateBoard(gameState); // Refresh the board display
        } else if (message.type === 'response') {
            alert(message.message); // Show response message
            updateStatus(message.current_turn); // Update the status display
            if (message.message === 'Game over') {
                // Handle game over scenario if needed
            }
        } else if (message.type === 'error') {
            alert(message.message); // Show error message
        }
    };

    // Function to initialize the game board
    function initializeBoard() {
        for (let row = 0; row < boardSize; row++) {
            gameState[row] = []; // Initialize row
            for (let col = 0; col < boardSize; col++) {
                gameState[row][col] = ''; // Initialize cell
                const cell = document.createElement('div'); // Create a new cell element
                cell.classList.add('cell'); // Add cell class
                cell.dataset.position = `${row},${col}`; // Set position data attribute
                cell.addEventListener('click', () => handleCellClick(cell)); // Add click event listener
                boardElement.appendChild(cell); // Add cell to the board
            }
        }
        sendDeployment(); // Send initial deployment of pieces
    }

    // Function to send initial deployment of pieces
    function sendDeployment() {
        const positions = ['P', 'P', 'P', 'H1', 'H2']; // Example positions for deployment
        sendMessage({ type: 'deploy', data: positions }); // Send deployment message
    }

    // Function to send a message via WebSocket
    function sendMessage(message) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message)); // Send message if connection is open
        } else {
            console.error('WebSocket connection is not open. Current state:', ws.readyState);
        }
    }

    // Function to update the game board display
    function updateBoard(gameState) {
        boardElement.innerHTML = ''; // Clear existing board content
        gameState.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                const cellElement = document.createElement('div'); // Create new cell element
                cellElement.className = 'cell'; // Add cell class
                if (cell) {
                    const [player, piece] = cell.split('-'); // Split cell data
                    cellElement.classList.add(`player-${player.toLowerCase()}`); // Add player class
                    cellElement.textContent = piece; // Set piece text content
                }
                cellElement.dataset.position = `${rowIndex},${colIndex}`; // Set position data attribute
                cellElement.addEventListener('click', () => handleCellClick(cellElement)); // Add click event listener
                boardElement.appendChild(cellElement); // Add cell to the board
            });
        });
    }

    // Function to handle cell click events
    function handleCellClick(cellElement) {
        const [row, col] = cellElement.dataset.position.split(',').map(Number); // Get cell position
        const piece = gameState[row][col]; // Get piece at cell position

        if (selectedPiece) {
            selectedPiece.classList.remove('selected'); // Deselect previously selected piece
            selectedPiece = null; // Clear selected piece
        }

        if (piece && piece.startsWith('A-')) { // If piece belongs to player A
            cellElement.classList.add('selected'); // Highlight selected piece
            selectedPiece = cellElement; // Set new selected piece
        }
    }

    // Function to handle piece movement
    function handleMove(direction) {
        if (!selectedPiece) {
            alert('Please select a piece first'); // Alert if no piece is selected
            return;
        }

        const [row, col] = selectedPiece.dataset.position.split(',').map(Number); // Get current position
        const piece = gameState[row][col]; // Get piece at current position
        const [player, pieceType] = piece.split('-'); // Split piece data

        let newCol;
        if (direction === 'left') {
            newCol = col - 1; // Move piece left
        } else if (direction === 'right') {
            newCol = col + 1; // Move piece right
        } else {
            return;
        }

        if (newCol < 0 || newCol >= boardSize) {
            alert('Invalid move: Out of bounds'); // Alert if move is out of bounds
            return;
        }

        const move = direction === 'left' ? 'L' : 'R'; // Determine move direction
        sendMove(`${pieceType}:${row},${col}`, move); // Send move command

        // Add move to history
        moveHistory.push(`${pieceType} moved ${direction}`);
        updateMoveHistory(); // Update move history display
    }

    // Function to send a move command via WebSocket
    function sendMove(character, move) {
        sendMessage({ type: 'move', data: { character, move } }); // Send move message
    }

    // Function to update the status display
    function updateStatus(currentTurn) {
        statusElement.textContent = `${currentTurn}'s turn`; // Update turn status
    }

    // Function to update the move history display
    function updateMoveHistory() {
        moveHistoryList.innerHTML = ''; // Clear existing move history
        moveHistory.forEach(move => {
            const li = document.createElement('li'); // Create new list item
            li.textContent = move; // Set list item text
            moveHistoryList.appendChild(li); // Add list item to history
        });
    }

    // Add event listeners for move buttons
    document.getElementById('move-left').addEventListener('click', () => handleMove('left')); // Move left
    document.getElementById('move-right').addEventListener('click', () => handleMove('right')); // Move right
});
