import copy
import logging

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand
from ..utils import probability_of_holding_area, probability_of_successful_attack, possible_attacks
from dicewars.ai.xrysav27.expmmnode import ExpMMNode
from dicewars.ai.xrysav27.player_controller import PlayerController
from dicewars.ai.xrysav27.model import Model


class AI:
    def __init__(self, player_name, board, players_order):
        self.board = None
        self.player_name = player_name
        self.players_order = players_order
        self.logger = logging.getLogger('AI')
        self.debugcounter = 0
        self.max_num_of_turn_first_level = 3  # graph width for our ai
        self.max_num_of_turn_variants = 1  # graph width for each player
        self.max_num_of_turns_per_player = 10  # graph height for each player
        self.player_controller = None
        self.win_rate_treshold = 0.8
        self.lose_rate_treshold = 0.3
        self.start_of_game = True
        self.model = Model()
        self.model.load()

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        self.logger.debug("Looking for possible turns.")
        self.board = board

        turns = self.possible_turns()

        # print("- {:.1f}".format(time_left), end=" - ")

        # little time left, so lets generate smaller tree
        if time_left < 5:
            self.max_num_of_turn_first_level = 2  # graph width for our ai
            self.max_num_of_turn_variants = 1  # graph width for each player
            # print("c", end=" - ")

        if time_left > 11:
            self.start_of_game = False

        # for first few turns we play as ste
        if time_left < 3 or self.start_of_game:
            # print("# STE")
            if len(turns) != 0:
                return BattleCommand(turns[0][0], turns[0][1])
        else:
            # print("# strom")
            if len(turns) != 0:
                turns = turns[:self.max_num_of_turn_first_level]

                best_return = -1
                best_return_turn = None
                root_node = ExpMMNode(self.board, nb_turns_this_game, self, self.model)

                self.player_controller = PlayerController(self.board, self.max_num_of_turns_per_player,
                                                          self.player_name, self.players_order)

                self.player_controller.i_just_played()

                for turn in turns:
                    board_after_battle_won, board_after_battle_lose = root_node.simulate_attack(turn[0], turn[1])
                    probability_of_win = turn[3]
                    actual_ret = 0
                    # 0.8
                    if probability_of_win > self.win_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, nb_turns_this_game, self, self.model)
                        actual_ret = next_node.exp_mm_rec(copy.deepcopy(self.player_controller))
                        # 0.3
                    elif probability_of_win > self.lose_rate_treshold:
                        next_node = ExpMMNode(board_after_battle_won, nb_turns_this_game, self, self.model)
                        actual_ret_won = probability_of_win * next_node.exp_mm_rec(
                            copy.deepcopy(self.player_controller))

                        next_node = ExpMMNode(board_after_battle_lose, nb_turns_this_game, self, self.model)
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

                return BattleCommand(attacker, defender)

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
            # hold_2_prob = hold_prob + 0.2 * probability_of_holding_area(board, area_name, 1, player_name)
            if hold_prob >= 0.2 or atk_power == 8:
                turns.append([area_name, target.get_name(), hold_prob, atk_prob])

        # print(len(turns))
        return sorted(turns, key=lambda turn: turn[2], reverse=True)
