# Vox Cards
This is an easy to use dependancy free deck manager, making it easy to develope the logic of
card games without worrying about creating ways to handle the decks, cards, and hands.

### Installation
Install using pip:
`py -m pip install vox_cards`

### Basic Usage
```Python
import vox_cards.deck as cards

deck = cards.Deck(2) # Pass the number of hands to construct this deck with.

deck.deal() # The default number of cards to deal is 7

player_1, player_2 = deck.hands

for card in player_1: # Print all cards in the first hand.
    print(card.full) # Prints the full name of the card (i.e. "10 of Clubs").
```
Keep in mind that hands are iterable, but only return the cards they hold.
With that in mind, there is also the ability for hands to draw and discard cards.
```Python
# This will draw the top 2 cards for each palyer, then discard 2 cards at random.
player_1.draw(2)
player_1.discard(2)

player_2.draw(2)
player_2.discard(2)


# You can also pass a card instance to hand.discard for discarding specific card(s).
player_1.discard(player_1.cards[0])
player_2.discard(player_2.cards[0])
```

##### More complex use case
Here is a more complex use case that features the main components of this module. It doesn't use any logic, but hopefully it gives you an idea of some use cases for this project.
```Python
import vox_cards.deck as cards

deck = cards.Deck(3)

for _ in range(3):
    deck.shuffle()

player_1, player_2, river = deck.hands

for _ in range(2):
    player_1.draw()
    player_2.draw()
    
river.draw(3)
river.draw()
river.draw()

print("\nPlayer 1's hand:")
for card in player_1:
    print(card.full)
    
print("\nPlayer 2's hand:")
for card in player_2:
    print(card.full)
    
print("\n\nAnd the river is:")
for card in river:
    print(card.full)
```

Here is the output for the code above:
```Python
>>>py example.py
Player 1's hand:
Queen of Spades
Jack of Spades

Player 2's hand:
6 of Clubs
8 of Spades


And the river is:
6 of Hearts
8 of Clubs
5 of Hearts
4 of Hearts
9 of Spades
```

Looks like player 2 wins with a 2-pair, how fitting.

### Documentation

<s>This entire project is still a WIP and has not been officially released yet.
Full documentation will come for this project whenever it has been released
in a stable state. Until then, refer to the usage examples and the github
repo for most use cases. </s>

For a full list of everything you can do, view the [docs](https://vox-cards.readthedocs.io/en/latest/)
