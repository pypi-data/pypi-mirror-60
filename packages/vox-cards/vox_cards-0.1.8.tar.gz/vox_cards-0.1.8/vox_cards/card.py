# builtins
from enum import Enum
import json

class Suit(Enum):
    """An Enumeration to make handling card suits easier.

    :param suit: A number between 0 and 4 denoting the suit, they are diamonds, clubs, hearts, spades, and joker respectively.
    :type Int: int
    :return: Returns an enum representing the suit. str(Suit) returns the titlecase representation of the suit name.
    :rtype: enum.Enum
    """


    DIAMONDS = 0
    CLUBS = 1
    HEARTS = 2
    SPADES = 3
    JOKER = 4

    def __str__(self):
        return self.name.title()
        


class Card:
    """A class that represents cards. Should only be created through the deck class, 
    however inheriting from this class to add additional functionality is encouraged.

    :param card_data: A :class:`Dict` with a suit and value.
    :type card_data: :class:`Dict`
    :return: A :class:`Card` object.
    :rtype: :class:`Card`

    Attributes
    ----------
    value: :class:`int`
        The integer representation of the cards value.
    suit: :class:`Suit`
        A :class:`Suit` enum denoting the cards suit.
    text: :class:`str`
        The string representation of the cards value. (i.e. A, 1, 2, etc.).
    full: :class:`str`
        The full name of the card (i.e. "Queen of Hearts")
    """
    def __init__(self, card_data):
        """Constructor method
        """
        self._data = card_data
        self.value = self._data["value"]
        self.suit = Suit(self._data["suit"])
        if self.value == 0:
            self.text = "Joker"
        elif self.value == 1:
            self.text = "Ace"
        elif self.value == 11:
            self.text = "Jack"
        elif self.value == 12:
            self.text = "Queen"
        elif self.value == 13:
            self.text = "King"
        else:
            self.text = str(self.value)
        self.full = f"{self.text} of {str(self.suit)}"
        
