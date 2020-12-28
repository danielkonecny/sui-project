import logging
from ..utils import possible_attacks
from ..utils import probability_of_holding_area, probability_of_successful_attack
import copy
import random

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class PlayerController:
    def __init__(self, board, max_turns_per_player, my_ai_name):
        self.board = board
        self.player_sequence = self.get_players_on_board()
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

    def search_player_sequence(self):
        # todo get player sequence, from game probably
        pass

    def get_player_sequence(self):
        return self.player_sequence

    def should_finish(self):
        return self.finish_recursion and (self.get_player_on_turn() == self.get_my_ai_name())


class ExpMMNode:
    def __init__(self, board, ai):
        self.board_copy = copy.deepcopy(board)
        self.nodes = None
        self.ai = ai
        self.win_rate_treshold = 0.7
        self.lose_rate_treshold = 0.3

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
            turns = self.ai.possible_turns(self.board_copy, simulated_player_this_turn)[
                    :self.ai.max_num_of_turn_variants]
            if len(turns) == 0:
                player_controller.i_skip()
                next_node = ExpMMNode(self.board_copy, self.ai)
                return next_node.exp_mm_rec(player_controller)
            else:
                return_sum = 0
                player_controller.i_just_played()
                sum_of_probabilities = 0
                for turn in turns:
                    board_after_battle_won, board_after_battle_lose = self.simulate_attack(turn[0], turn[1])
                    probability_of_win = turn[3]
                    # 0.7
                    if probability_of_win > self.win_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self.ai)
                        return_sum += probability_of_win * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += probability_of_win
                        # 0.3
                    elif probability_of_win > self.lose_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self.ai)
                        return_sum += probability_of_win * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += probability_of_win

                        next_node = ExpMMNode(board_after_battle_lose, self.ai)
                        return_sum += (1 - probability_of_win) * next_node.exp_mm_rec(copy.deepcopy(player_controller))
                        sum_of_probabilities += 1 - probability_of_win

                if sum_of_probabilities != 0:
                    return_average = return_sum / sum_of_probabilities
                    return return_average
                else:
                    return 0

    def calculate_heuristic(self, player):
        players_regions = self.board_copy.get_players_regions(player)
        max_region_size = max(len(region) for region in players_regions)
        nb_of_areas = len(self.board_copy.get_player_areas(player))
        nb_of_dice = self.board_copy.get_player_dice(player)
        return max_region_size


class AI:
    """Agent using Single Turn Expectiminimax (STE) strategy

    This agent makes such moves that have a probability of successful
    attack and hold over the area until next turn higher than 20 %.
    """

    def __init__(self, player_name, board, players_order):
        """
        Parameters
        ----------
        game : Game
        """
        self.player_name = player_name
        self.logger = logging.getLogger('AI')
        self.debugcounter = 0
        self.max_num_of_turn_first_level = 3  # graph width for our ai
        self.max_num_of_turn_variants = 1  # graph width for each player
        self.max_num_of_turns_per_player = 10  # graph height for each player
        self.player_controller = None
        self.win_rate_treshold = 0.8
        self.lose_rate_treshold = 0.3

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn

        Agent gets a list preferred moves and makes such move that has the
        highest estimated hold probability. If there is no such move, the agent
        ends it's turn.
        """
        self.logger.debug("Looking for possible turns.")
        self.board = board
        # turns = self.possible_turns()[:self.max_num_of_turn_variants]
        turns = self.possible_turns()[:self.max_num_of_turn_first_level]
        self.player_controller = PlayerController(self.board, self.max_num_of_turns_per_player, self.player_name)

        # print(self.player_controller.get_player_sequence())
        if time_left > 2:
            i = 0
            if len(turns) != 0:
                best_return = -1
                best_return_turn = None
                root_node = ExpMMNode(self.board, self)
                self.player_controller.i_just_played()

                for turn in turns:
                    board_after_battle_won, board_after_battle_lose = root_node.simulate_attack(turn[0], turn[1])
                    probability_of_win = turn[3]
                    actual_ret = 0
                    # 0.8
                    if probability_of_win > self.win_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self)
                        actual_ret = next_node.exp_mm_rec(copy.deepcopy(self.player_controller))
                        # 0.3
                    elif probability_of_win > self.lose_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, self)
                        actual_ret_won = probability_of_win * next_node.exp_mm_rec(
                            copy.deepcopy(self.player_controller))

                        next_node = ExpMMNode(board_after_battle_lose, self)
                        actual_ret_lose = (1 - probability_of_win) * next_node.exp_mm_rec(
                            copy.deepcopy(self.player_controller))

                        actual_ret = actual_ret_won + actual_ret_lose

                    if actual_ret > best_return:
                        best_return_turn = turn

                attacker = best_return_turn[0]
                defender = best_return_turn[1]
                self.logger.debug("Possible turn: {}".format(best_return_turn))
                hold_prob = best_return_turn[2]
                self.logger.debug(
                    "{0}->{1} attack and hold probabiliy {2}".format(attacker, defender, hold_prob))

                if attacker != turns[0][0] and defender != turns[0][1]:
                    pass
                return BattleCommand(attacker, defender)
        else:
            if len(turns) != 0:
                return BattleCommand(turns[0][0], turns[0][1])

        self.logger.debug("No more plays.")
        return EndTurnCommand()

    def possible_turns(self, board=None, player_name=None):
        """Get a list of preferred moves

        This list is sorted with respect to hold probability in descending order.
        It includes all moves that either have hold probability higher or equal to 20 %
        or have strength of eight dice.
        """
        if player_name is None:
            player_name = self.player_name

        if board is None:
            board = self.board

        turns = []

        for source, target in possible_attacks(board, player_name):
            area_name = source.get_name()
            atk_power = source.get_dice()
            atk_prob = probability_of_successful_attack(board, area_name, target.get_name())
            hold_prob = atk_prob * probability_of_holding_area(board, target.get_name(), atk_power - 1,
                                                               player_name)
            hold_2_prob = hold_prob + 0.2 * probability_of_holding_area(board, area_name, 1, player_name)
            if hold_prob >= 0.2 or atk_power == 8:
                turns.append([area_name, target.get_name(), hold_prob, atk_prob])

        # print(len(turns))
        return sorted(turns, key=lambda turn: turn[2], reverse=True)
