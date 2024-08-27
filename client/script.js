document.addEventListener('DOMContentLoaded', () => {
    const boardSize = 5;
    const boardElement = document.getElementById('game-board');
    const statusElement = document.getElementById('status');
    const moveHistoryList = document.getElementById('move-history-list');
    const ws = new WebSocket('ws://localhost:8765/A');  // Connect as player A

    let gameState = [];
    let selectedPiece = null;
    let moveHistory = [];

    ws.onopen = function() {
        console.log('WebSocket connection established');
        initializeBoard();
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    ws.onclose = function(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
    };

    ws.onmessage = function(event) {
        console.log('Received message:', event.data);
        const message = JSON.parse(event.data);
        if (message.type === 'state_update') {
            gameState = message.data;
            updateBoard(gameState);
        } else if (message.type === 'response') {
            alert(message.message);
            updateStatus(message.current_turn);
            if (message.message === 'Game over') {
            }
        } else if (message.type === 'error') {
            alert(message.message);
        }
    };

    function initializeBoard() {
        for (let row = 0; row < boardSize; row++) {
            gameState[row] = [];
            for (let col = 0; col < boardSize; col++) {
                gameState[row][col] = '';
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.position = `${row},${col}`;
                cell.addEventListener('click', () => handleCellClick(cell));
                boardElement.appendChild(cell);
            }
        }
        sendDeployment();
    }

    function sendDeployment() {
        const positions = ['P', 'P', 'P', 'H1', 'H2']; 
        sendMessage({ type: 'deploy', data: positions });
    }

    function sendMessage(message) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        } else {
            console.error('WebSocket connection is not open. Current state:', ws.readyState);
        }
    }

    function updateBoard(gameState) {
        boardElement.innerHTML = '';
        gameState.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                const cellElement = document.createElement('div');
                cellElement.className = 'cell';
                if (cell) {
                    const [player, piece] = cell.split('-');
                    cellElement.classList.add(`player-${player.toLowerCase()}`);
                    cellElement.textContent = piece;
                }
                cellElement.dataset.position = `${rowIndex},${colIndex}`;
                cellElement.addEventListener('click', () => handleCellClick(cellElement));
                boardElement.appendChild(cellElement);
            });
        });
    }

    function handleCellClick(cellElement) {
        const [row, col] = cellElement.dataset.position.split(',').map(Number);
        const piece = gameState[row][col];

        if (selectedPiece) {
            selectedPiece.classList.remove('selected');
            selectedPiece = null;
        }

        if (piece && piece.startsWith('A-')) {
            cellElement.classList.add('selected');
            selectedPiece = cellElement;
        }
    }

    function handleMove(direction) {
        if (!selectedPiece) {
            alert('Please select a piece first');
            return;
        }

        const [row, col] = selectedPiece.dataset.position.split(',').map(Number);
        const piece = gameState[row][col];
        const [player, pieceType] = piece.split('-');

        let newCol;
        if (direction === 'left') {
            newCol = col - 1;
        } else if (direction === 'right') {
            newCol = col + 1;
        } else {
            return;
        }

        if (newCol < 0 || newCol >= boardSize) {
            alert('Invalid move: Out of bounds');
            return;
        }

        const move = direction === 'left' ? 'L' : 'R';
        sendMove(`${pieceType}:${row},${col}`, move);

        // Add move to history
        moveHistory.push(`${pieceType} moved ${direction}`);
        updateMoveHistory();
    }

    function sendMove(character, move) {
        sendMessage({ type: 'move', data: { character, move } });
    }

    function updateStatus(currentTurn) {
        statusElement.textContent = `${currentTurn}'s turn`;
    }

    function updateMoveHistory() {
        moveHistoryList.innerHTML = '';
        moveHistory.forEach(move => {
            const li = document.createElement('li');
            li.textContent = move;
            moveHistoryList.appendChild(li);
        });
    }

    // Add event listeners for move buttons
    document.getElementById('move-left').addEventListener('click', () => handleMove('left'));
    document.getElementById('move-right').addEventListener('click', () => handleMove('right'));
});
