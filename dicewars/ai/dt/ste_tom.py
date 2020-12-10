import logging
from ..utils import possible_attacks
from ..utils import probability_of_holding_area, probability_of_successful_attack
import copy
import random

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class ExpMMNode:
    def __init__(self, board, ai):
        self.board_copy = copy.deepcopy(board)
        self.nodes = None
        self.ai = ai

    # vykradl jsem z dicewars/client/ai_driver.py - handle_server_message
    def simulate_attack(self, from_data, to_data):
        attacker = self.board_copy.get_area(from_data)
        defender = self.board_copy.get_area(to_data)

        attacker_dice = attacker.get_dice()
        defender_dice = defender.get_dice()

        attacker_pwr = 0
        defender_pwr = 0

        for i in range(0, attacker_dice):
            attacker_pwr += random.randint(1, 6)
        for i in range(0, defender_dice):
            defender_pwr += random.randint(1, 6)

        attacker.set_dice(1)
        if attacker_pwr > defender_pwr:
            print("fajt won")
            defender.set_dice(attacker_dice - 1)
            defender.set_owner(attacker.get_owner_name())
        else:
            print("fajt lost")

        # self.game.players[atk_name].set_score(msg['score'][str(atk_name)])
        # self.game.players[def_name].set_score(msg['score'][str(def_name)])

    def exp_mm_rec(self, board):
        if player_on_turn == calling_player: #TODO
            # evaluate probability
            # pocet kostek na desce
            # TODO
            return
        else:
            # recursion
            # tohle mus9 b7t pro konkr0tn9ho hr84e
            turns = self.ai.possible_turns(board, player_on_turn)[:self.ai.max_num_of_turn_variants]
            if len(turns) == 0:
                # EndTurnCommand
                return

            return_sum = 0
            for turn in turns:
                next_node = ExpMMNode(board, self)
                return_sum += next_node.exp_mm_rec(None)

            return_average = return_sum / len(turns)
            return return_average

            node_score = 0
            for node in p1.nodes:
                node_score = node_score + self.ai.exp_mm_rec(self, node.board, player_on_turn++, calling_player)


            node_average = node_score / size(p1.nodes)

            p1.simulate_attack(turns[0][0], turns[0][1])
            self.ai.ai_turn(p1.board_copy)

            # self.exp_mm_rec(player_on_turn++, calling_player)

    def get_next_player(self):



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
        self.max_num_of_turn_variants = 3    # graph width for each player
        self.max_num_of_turns_per_player = 2 # graph height for each player

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn

        Agent gets a list preferred moves and makes such move that has the
        highest estimated hold probability. If there is no such move, the agent
        ends it's turn.
        """
        self.logger.debug("Looking for possible turns.")
        self.board = board
        turns = self.possible_turns()[:self.ai.max_num_of_turn_variants]

        best_return = 0
        best_return_turn = None
        return_sum = 0
        for turn in turns:
            next_node = ExpMMNode(board, self)
            actual_ret = next_node.exp_mm_rec(None)
            return_sum += actual_ret
            if act_ret > best_return:
                best_return_turn = turn

        ret = p1.exp_mm_rec(self.board, player_on_turn, calling_player)

        # turns - 2,6,8,10
        # vezmeme 2 nejlepsi a udelame pro ne expmm na jedno kolo (2 nejlepsi tahy (podle ste) kazdy)

        # if(self.debugcounter == 0):
        #     print("puvodni")
        #     print(self.board)
        #     for key, area in self.board.areas.items():
        #         print(f"{key}:\t{area.owner_name} - {area.dice} - {area.neighbours}")
        #
        #     p1 = ExpMMNode(self.board, self)
        #     print("upravena")
        #     # print(turns)
        #     if len(turns) > 0:
        #         self.debugcounter += 1
        #         print("udelam vsechno")
        #         p1.simulate_attack(turns[0][0], turns[0][1])
        #         for key, area in p1.board_copy.areas.items():
        #             print(f"{key}:\t{area.owner_name} - {area.dice} - {area.neighbours}")
        #         print("odkud: ", turns[0][0])
        #         print("kampak: ", turns[0][1])
        #     else:
        #         print("nebudu delat nic!")

        if turns:
            turn = turns[0]
            area_name = turn[0]
            self.logger.debug("Possible turn: {}".format(turn))
            hold_prob = turn[2]
            self.logger.debug("{0}->{1} attack and hold probabiliy {2}".format(area_name, turn[1], hold_prob))

            return BattleCommand(area_name, turn[1])

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
            hold_2_prob = hold_prob * probability_of_holding_area(board, area_name, 1, player_name)
            if hold_prob >= 0.2 or atk_power == 8:
                turns.append([area_name, target.get_name(), hold_prob])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)

    def testovaci(self):
        print("hura")
