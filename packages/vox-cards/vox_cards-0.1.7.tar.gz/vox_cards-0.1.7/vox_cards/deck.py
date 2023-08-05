# builtins
import random
import json
import os

# locals
from .card import Card
from .hand import Hand

def generate_card_data():
    """Generates card data for the class:`Card` class.

    :return: dict objects with 'suit' and 'value' keys.
    :rtype: dict
    """
    suits = 3
    values = 13
    cur_suit = 0
    cur_value = 1
    while cur_suit <= suits and cur_value <= values:
        yield {"suit":cur_suit, "value":cur_value}
        if cur_value == values:
            cur_suit += 1
            cur_value = 0
        cur_value += 1
        

JOKER = {"suit": 4, "value": 0}




class Deck:
    """A class allowing the control of hands, and storing the cards used.

    :param hands: The number of hands to construct the deck with.
    :type hands: int
    :param jokers: Whether or not to construct the deck with 2 additional joker cards.
    :type jokers: bool
    :return: Returns a deck object that is iterable.
    :rtype: Deck
    """

    default_deck = [Card(d) for d in generate_card_data()]
    joker = Card(JOKER)

    def __init__(self, hands=1, jokers=False):
        """Constructor method
        """
        self.cards = Deck.default_deck
        if jokers:
            self.cards += [Deck.joker]*2
        self.hands = [Hand(self) for _ in range(hands)] 
        self.drawn_cards = []
        self.discarded_cards = []
        self.is_shuffled = False

        

    def deal(self, amount=7):
        """Deals [amount] cards to all hands.

        :param amount: Amount of cards to deal to players, defaults to 7
        :type amount: int (, optional)
        """
        for _ in range(amount):
            for hand in self.hands:
                hand.draw()

    def shuffle(self, new_deck=False):
        """Shuffle the deck in place.

        :param new_deck: Whether or nor to reset the deck back to it's original state, removing all cards from hands, and setting drawn_cards and discarded cards back to empty lists.
        :type new_deck: bool (, optional)
        """

        if new_deck:
            for hand in self.hands:
                hand.discard(hand.card_count)
            self.cards += self.discarded_cards
            self.discarded_cards = []
            self.drawn_cards = []
            self.cards = Deck.default_deck
        
        cards = list(self.cards)
        random.shuffle(cards)
        self.is_shuffled = True
        self.cards = cards

    def __iter__(self):
        return iter(self.cards)
            