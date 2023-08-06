# builtins
import random
import json
import os

# locals
from .card import Card
from .hand import Hand

def generate_card_data():
    """Generates card data for the class:`Card` class.

    :return: :class:`dict` objects with 'suit' and 'value' keys.
    :rtype: :class:`dict`
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
    :type hands: :class:`int`
    :param jokers: Whether or not to construct the deck with 2 additional joker cards.
    :type jokers: :class:`bool`
    :return: Returns a :class:`Deck` object that is iterable.
    :rtype: :class:`Deck`

    Attributes
    ----------
    cards: :class:`list`
        The full list of :class:`Card` objects that :class:`Hand` objects draw from.
    hands: :class:`list`
        A list of :class:`Hand` objects that belong to this deck and can draw from it.
    drawn_cards: :class:`list`
        A list of :class:`Card` objects that have already been removed from
        self.cards by either dealing to self.hands or having hands draw from
        this deck. Typically, unless influenced, all cards found in this list
        will always also be in a :class:`Hand`
    discarded_cards: :class:`list`
        A list of :class:`Card` objects that have been discarded via the
        hand.discard method.
    is_shuffled: :class:`bool`
        Denotes whether or not the deck has been shuffled via the :class:`Deck`.shuffle method.
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

        :param amount: Amount of :class:`Card` objects to deal to :attr:`~Deck.hands`, defaults to 7
        :type amount: :class:`int` (, optional)
        """
        for _ in range(amount):
            for hand in self.hands:
                hand.draw()

    def shuffle(self, new_deck=False):
        """Shuffle the deck in place.

        :param new_deck: Whether or nor to reset the deck back to it's original state, 
        removing all cards from :class:`Hand` objects in :attr:`~Deck.hands`, 
        and setting :attr:`~Deck.drawn_cards` and :attr:`Deck.discarded_cards` to empty lists.
        :type new_deck: :class:`bool` (, optional)
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
            