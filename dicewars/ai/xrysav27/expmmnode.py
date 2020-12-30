import copy


class ExpMMNode:
    def __init__(self, board, nb_turns_this_game, ai, model):
        self.board_copy = copy.deepcopy(board)
        self.nb_turns_this_game = nb_turns_this_game
        self.nodes = None
        self.ai = ai
        self.win_rate_treshold = 0.7
        self.lose_rate_treshold = 0.3
        self.model = model

    # vykradl jsem z dicewars/client/ai_driver.py - handle_server_message
    def simulate_attack(self, from_data, to_data):
        board_after_battle = copy.deepcopy(self.board_copy)

        attacker = board_after_battle.get_area(from_data)
        defender = board_after_battle.get_area(to_data)

        attacker_dice = attacker.get_dice()

        # battle lose
        attacker.set_dice(1)
        board_after_battle_lose = copy.deepcopy(board_after_battle)

        # battle won
        defender.set_dice(attacker_dice - 1)
        defender.set_owner(attacker.get_owner_name())
        board_after_battle_won = board_after_battle

        return board_after_battle_won, board_after_battle_lose

    def exp_mm_rec(self, player_controller):
        if player_controller.should_finish():
            return self.calculate_heuristic(player_controller.get_my_ai_name())
        else:
            # recursion
            simulated_player_this_turn = player_controller.get_player_on_turn()
            turns = self.ai.possible_turns(self.board_copy, simulated_player_this_turn)
            if len(turns) == 0:
                player_controller.i_skip()
                next_node = ExpMMNode(self.board_copy, self.nb_turns_this_game, self.ai, self.model)
                return next_node.exp_mm_rec(player_controller)
            else:
                turns = turns[:self.ai.max_num_of_turn_variants]
                return_sum = 0
                player_controller.i_just_played()
                sum_of_probabilities = 0
                for turn in turns:
                    board_after_battle_won, board_after_battle_lose = self.simulate_attack(turn[0], turn[1])
                    probability_of_win = turn[3]
                    # 0.7
                    if probability_of_win > self.win_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self.nb_turns_this_game, self.ai, self.model)
                        return_sum += probability_of_win * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += probability_of_win
                        # 0.3
                    elif probability_of_win > self.lose_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self.nb_turns_this_game, self.ai, self.model)
                        return_sum += probability_of_win * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += probability_of_win

                        next_node = ExpMMNode(board_after_battle_lose, self.nb_turns_this_game, self.ai, self.model)
                        return_sum += (1 - probability_of_win) * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += 1 - probability_of_win

                if sum_of_probabilities != 0:
                    return_average = return_sum / sum_of_probabilities
                    return return_average
                else:
                    return 0

    def calculate_heuristic(self, player):
        players_regions = self.board_copy.get_players_regions(player)
        score = 0
        if players_regions is not None:
            score = max(len(region) for region in players_regions) / 29
        # nb_of_areas = len(self.board_copy.get_player_areas(player))
        # nb_of_dice = self.board_copy.get_player_dice(player)

        win_probabilities = self.model.predict_board(self.board_copy, self.nb_turns_this_game)

        win = 0
        if win_probabilities is not None:
            win = win_probabilities[player - 1]

        if win > 0.001:
            probability = 0.3 * score + 0.7 * win
        else:
            probability = score

        return probability
