class Game:
    def __init__(self):
        # Initialize the game state with an empty 5x5 grid
        self.game_state = [
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', '']
        ]
        self.current_turn = 'A'  # Start with player 'A'
        self.player_positions = {'A': [], 'B': []}  # Track positions of pieces for each player
        self.player_char_count = {'A': {'P': 0, 'H1': 0, 'H2': 0}, 'B': {'P': 0, 'H1': 0, 'H2': 0}}  # Count pieces for each player

    def get_game_state(self):
        # Return the current game state
        return self.game_state

    def deploy_characters(self, player, positions):
        # Deploy characters for a player to the board
        if len(positions) != 5:
            return False  # Deployment must include exactly 5 characters
        row = 0 if player == 'A' else 4  # 'A' deploys at the top row, 'B' at the bottom row
        self.player_char_count[player] = {'P': positions.count('P'), 'H1': positions.count('H1'), 'H2': positions.count('H2')}
        
        # Check if the correct number of each character type is deployed
        if (self.player_char_count[player]['P'] != 3 or
            self.player_char_count[player]['H1'] != 1 or
            self.player_char_count[player]['H2'] != 1):
            return False
        
        # Place the characters on the board
        for i, char in enumerate(positions):
            self.game_state[row][i] = f"{player}-{char}"
            self.player_positions[player].append((row, i, char))
        return True
    
    def process_move(self, player, character, move):
        # Process a move for a player
        if self.current_turn != player:
            return "Not your turn"  # Ensure it's the player's turn
        
        char_name, move_dir = character.split(':')[0], move  # Split character name and move direction
        char_pos = None
        # Find the character's current position on the board
        for r_idx, row in enumerate(self.game_state):
            if f"{player}-{char_name}" in row:
                char_pos = (r_idx, row.index(f"{player}-{char_name}"))
                break
        
        if not char_pos:
            return "Character not found"  # Character must be on the board to move
        
        # Map move directions to row/column changes
        direction_map = {
            'L': (0, -1), 'R': (0, 1), 'F': (-1, 0), 'B': (1, 0),
            'FL': (-1, -1), 'FR': (-1, 1), 'BL': (1, -1), 'BR': (1, 1)
        }
        
        if move_dir not in direction_map:
            return "Invalid move direction"  # Ensure move direction is valid
        
        row_delta, col_delta = direction_map[move_dir]
        new_pos = (char_pos[0] + row_delta, char_pos[1] + col_delta)  # Calculate new position
        
        # Check if the new position is within board boundaries
        if not (0 <= new_pos[0] < 5 and 0 <= new_pos[1] < 5):
            return "Move out of bounds"
        
        target_cell = self.game_state[new_pos[0]][new_pos[1]]
        if target_cell.startswith(player):
            return "Move targets friendly character"  # Cannot move to a cell occupied by the same player
        
        if self.game_state[new_pos[0]][new_pos[1]] != '':
            if char_name.startswith('H'):
                # If moving a 'H' character, remove opponent characters in the path
                path = self._get_path(char_pos, new_pos, direction_map[move_dir])
                for pos in path:
                    if self.game_state[pos[0]][pos[1]].startswith(self._get_opponent(player)):
                        self.game_state[pos[0]][pos[1]] = ''
            else:
                # For other characters, simply replace the target cell content
                self.game_state[new_pos[0]][new_pos[1]] = f"{player}-{char_name}"
        
        # Clear the old position and switch turns
        self.game_state[char_pos[0]][char_pos[1]] = ''
        self._switch_turn()
        
        # Check if the game is over
        if self.is_game_over():
            return "Game over"
        
        return "Move successful"
    
    def _get_path(self, start_pos, end_pos, direction):
        # Compute the path from start_pos to end_pos in the given direction
        path = []
        current = start_pos
        while current != end_pos:
            path.append(current)
            current = (current[0] + direction[0], current[1] + direction[1])
        return path
    
    def _switch_turn(self):
        # Switch the turn to the other player
        self.current_turn = 'B' if self.current_turn == 'A' else 'A'
    
    def is_game_over(self):
        # Check if either player has no characters left
        return not self.player_positions['A'] or not self.player_positions['B']

    def _get_opponent(self, player):
        # Return the opponent of the given player
        return 'B' if player == 'A' else 'A'
