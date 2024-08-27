class Game:
    def __init__(self):
        # Initialize game state
        self.game_state = [
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', '']
        ]
        self.current_turn = 'A'
        self.player_positions = {'A': [], 'B': []}
        self.player_char_count = {'A': {'P': 0, 'H1': 0, 'H2': 0}, 'B': {'P': 0, 'H1': 0, 'H2': 0}}
    
    def get_game_state(self):
        return self.game_state

    def deploy_characters(self, player, positions):
        if len(positions) != 5:
            return False
        row = 0 if player == 'A' else 4
        self.player_char_count[player] = {'P': positions.count('P'), 'H1': positions.count('H1'), 'H2': positions.count('H2')}
        
        if (self.player_char_count[player]['P'] != 3 or
            self.player_char_count[player]['H1'] != 1 or
            self.player_char_count[player]['H2'] != 1):
            return False
        
        for i, char in enumerate(positions):
            self.game_state[row][i] = f"{player}-{char}"
            self.player_positions[player].append((row, i, char))
        return True
    
    def process_move(self, player, character, move):
        if self.current_turn != player:
            return "Not your turn"
        
        char_name, move_dir = character.split(':')[0], move
        char_pos = None
        for r_idx, row in enumerate(self.game_state):
            if f"{player}-{char_name}" in row:
                char_pos = (r_idx, row.index(f"{player}-{char_name}"))
                break
        
        if not char_pos:
            return "Character not found"
        
        direction_map = {
            'L': (0, -1), 'R': (0, 1), 'F': (-1, 0), 'B': (1, 0),
            'FL': (-1, -1), 'FR': (-1, 1), 'BL': (1, -1), 'BR': (1, 1)
        }
        
        if move_dir not in direction_map:
            return "Invalid move direction"
        
        row_delta, col_delta = direction_map[move_dir]
        new_pos = (char_pos[0] + row_delta, char_pos[1] + col_delta)
        
        if not (0 <= new_pos[0] < 5 and 0 <= new_pos[1] < 5):
            return "Move out of bounds"
        
        target_cell = self.game_state[new_pos[0]][new_pos[1]]
        if target_cell.startswith(player):
            return "Move targets friendly character"
        
        if self.game_state[new_pos[0]][new_pos[1]] != '':
            if char_name.startswith('H'):
                # Remove all opponent characters in path
                path = self._get_path(char_pos, new_pos, direction_map[move_dir])
                for pos in path:
                    if self.game_state[pos[0]][pos[1]].startswith(self._get_opponent(player)):
                        self.game_state[pos[0]][pos[1]] = ''
            else:
                # Normal move, just replace character
                self.game_state[new_pos[0]][new_pos[1]] = f"{player}-{char_name}"
        
        self.game_state[char_pos[0]][char_pos[1]] = ''
        self._switch_turn()
        
        if self.is_game_over():
            return "Game over"
        
        return "Move successful"
    
    def _get_path(self, start_pos, end_pos, direction):
        path = []
        current = start_pos
        while current != end_pos:
            path.append(current)
            current = (current[0] + direction[0], current[1] + direction[1])
        return path
    
    def _switch_turn(self):
        self.current_turn = 'B' if self.current_turn == 'A' else 'A'
    
    def is_game_over(self):
        return not self.player_positions['A'] or not self.player_positions['B']

    def _get_opponent(self, player):
        return 'B' if player == 'A' else 'A'
