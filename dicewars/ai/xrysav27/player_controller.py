class PlayerController:
    def __init__(self, board, max_turns_per_player, my_ai_name, players_order):
        self.board = board
        self.player_sequence = self.get_player_sequence(players_order)
        self.actual_player_nb_turns = 0
        self.max_turns_per_player = max_turns_per_player
        self.player_on_turn = my_ai_name
        self.player_count = len(self.player_sequence)
        self.finish_recursion = 0
        self.my_ai_name = my_ai_name

    def get_my_ai_name(self):
        return self.my_ai_name

    def get_next_player(self):
        self.finish_recursion = 1
        actual_player_order = self.player_sequence.index(self.player_on_turn)
        next_player_order = actual_player_order + 1
        if next_player_order >= self.player_count:
            next_player_order = 0
        return self.player_sequence[next_player_order]

    def get_player_on_turn(self):
        return self.player_on_turn

    def i_just_played(self):
        self.actual_player_nb_turns += 1
        if self.actual_player_nb_turns == self.max_turns_per_player:
            self.actual_player_nb_turns = 0
            self.player_on_turn = self.get_next_player()

    def i_skip(self):
        self.player_on_turn = self.get_next_player()
        self.actual_player_nb_turns = 0

    def get_players_on_board(self):
        players = []
        for area in self.board.areas:
            area_owner = self.board.get_area(area).get_owner_name()
            players.append(area_owner) if area_owner not in players else players
        return players

    def get_player_sequence(self, players_order):
        players_on_board = self.get_players_on_board()
        # filter only alive players from players order
        alive_players_sequence = [i for i in players_order if i in players_on_board]
        return alive_players_sequence

    def should_finish(self):
        return self.finish_recursion and (self.get_player_on_turn() == self.get_my_ai_name())
