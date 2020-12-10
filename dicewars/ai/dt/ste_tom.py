import logging
from ..utils import possible_attacks
from ..utils import probability_of_holding_area, probability_of_successful_attack
import copy
import random

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class ExpMMNode:
    def __init__(self, board, ai_copy):
        self.left = None
        self.board_copy = copy.deepcopy(board)
        # self.right = None
        # self.value = None
        self.ai_copy = ai_copy

    def count_next_lr(self):
        board_copy = copy.deepcopy(self.board)

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

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn

        Agent gets a list preferred moves and makes such move that has the
        highest estimated hold probability. If there is no such move, the agent
        ends it's turn.
        """
        self.logger.debug("Looking for possible turns.")
        self.board = board
        turns = self.possible_turns()
        # turns - 2,6,8,10
        # vezmeme 2 nejlepsi a udelame pro ne expmm na jedno kolo (2 nejlepsi tahy (podle ste) kazdy)
        # p1 = ExpMMNode(self.board, self)
        # if len(turns) >= 2:
            # p1.left = turns[0]
            # p1.right = turns[1]
            # print(self)
            # print(p1.ai_copy)
        # p1.count_next_lr()

        if(self.debugcounter == 0):


            print("puvodni")
            print(self.board)
            for key, area in self.board.areas.items():
                print(f"{key}:\t{area.owner_name} - {area.dice} - {area.neighbours}")

            p1 = ExpMMNode(self.board, self)
            print("upravena")
            # print(turns)
            if len(turns) > 0:
                self.debugcounter += 1
                print("udelam vsechno")
                p1.simulate_attack(turns[0][0], turns[0][1])
                for key, area in p1.board_copy.areas.items():
                    print(f"{key}:\t{area.owner_name} - {area.dice} - {area.neighbours}")
                print("odkud: ", turns[0][0])
                print("kampak: ", turns[0][1])
            else:
                print("nebudu delat nic!")

        if turns:
            turn = turns[0]
            area_name = turn[0]
            self.logger.debug("Possible turn: {}".format(turn))
            hold_prob = turn[2]
            self.logger.debug("{0}->{1} attack and hold probabiliy {2}".format(area_name, turn[1], hold_prob))

            return BattleCommand(area_name, turn[1])

        self.logger.debug("No more plays.")
        return EndTurnCommand()

    def possible_turns(self):
        """Get a list of preferred moves

        This list is sorted with respect to hold probability in descending order.
        It includes all moves that either have hold probability higher or equal to 20 %
        or have strength of eight dice.
        """
        turns = []

        for source, target in possible_attacks(self.board, self.player_name):
            area_name = source.get_name()
            atk_power = source.get_dice()
            atk_prob = probability_of_successful_attack(self.board, area_name, target.get_name())
            hold_prob = atk_prob * probability_of_holding_area(self.board, target.get_name(), atk_power - 1, self.player_name)
            hold_2_prob = hold_prob * probability_of_holding_area(self.board, area_name, 1, self.player_name)
            if hold_prob >= 0.2 or atk_power == 8:
                turns.append([area_name, target.get_name(), hold_prob])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)

    def testovaci(self):
        print("hura")
