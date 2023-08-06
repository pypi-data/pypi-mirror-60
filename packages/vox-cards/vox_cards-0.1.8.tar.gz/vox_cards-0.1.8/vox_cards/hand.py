# builtins
import random

# locals
from .card import Card

class Hand:
    """A hand class that gives functionality to drawing, discarding, and holding cards from a deck. 
    This class should typically not be created, but inheriting from this class to give extended 
    functionality to a player class is encouraged. You cand replace the Deck().hands property
    with a list of your player classes.

    :param deck: the deck that this hand belongs to
    :type deck: Deck
    :return: A Hand class that is iterable.
    :rtype: Hand

    Attributes
    ----------
    cards: :class:`list`
        The cards currently held in this hand.
    deck: :class:`Deck`
        The deck that this hand is playing from. This is set when the hand is created
        in the Deck constructor and should not be reassigned.
    """
    def __init__(self, deck):
        """Constructor method
        """
        self.cards = []
        self.deck = deck

        self.is_dealer = False
        # TODO:
        # Add functionality to Deck to not deal to
        # hands that have this flag enabled to make it
        # easier to deal to multiple players when one acts
        # as a dealer/house/board.

        # properties
        self._card_count = len(self.cards)
    
    def __iter__(self):
        return iter(self.cards)

    @property
    def card_count(self):
        """The number of cards in this hand.

        :return: The length of hand.cards
        :rtype: int
        """
        self._card_count = len(self.cards)
        return self._card_count

    def discard(self, to_discard=1):
        """Remove [to_discard] amount of cards fromt his hand at random and add them to hand.deck.discarded_cards list.

        :param to_discard: Amount of cards to discard, defaults to 1
        :type to_discard: int (, optional)
        """
        if type(to_discard) == int:
            if to_discard == self.card_count:
                self.deck.discarded_cards += self.cards
                self.cards = []
            else:
                for _ in range(to_discard):
                    self.deck.discarded_cards.append(
                        self.cards.pop(
                            random.randint(0, len(self.cards)-1)
                        )
                    )
        elif type(to_discard) == Card:
            try:
                self.deck.discarded_cards.append(
                    self.cards.pop(
                        self.cards.index(to_discard)
                    )
                )
            except ValueError as e:
                print(e)



    def draw(self, amount=1):
        """Simulates drawing [amount] of cards from the top of the deck, rather then getting a random card.

        :param amount: Number of cards to draw, defaults to 1
        :type amount: int (, optional)
        :return: Returns the card(s) that were drawn.
        :rtype: list of Card
        """
        cards = []
        for _ in range(amount):
            card = self.deck.cards.pop()
            self.deck.drawn_cards.append(card)
            self.cards.append(card)
            cards.append(card)
        return cards
