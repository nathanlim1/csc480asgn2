from Poker import Poker
import itertools
import math, random, time

C = math.sqrt(2)

class LeafNode:
    def __init__(self):
        self.wins = 0
        self.playouts = 0
    def ucb1(self, total_playouts):
        if self.playouts == 0 or total_playouts == 0:
            return float("inf")
        return self.wins / self.playouts + C * math.sqrt(math.log(total_playouts) / self.playouts)

def get_unknown_cards(game):
    """Returns the cards that are not known to the player."""
    unknown_cards = []
    for card in game.deck:
        if card not in game.player_1_hand and card not in game.community_cards:
            unknown_cards.append(card)
    return unknown_cards

def rollout(game, opponent_hand):
    """Perform a rollout with a given opponent hand."""
    # Copy the game state
    simulation = game.copy_with_random_state()

    # Deal the opponent's hand
    simulation.player_2_hand = opponent_hand

    # Remove the opponent's hand from the deck
    for card in opponent_hand:
        simulation.deck.remove(card)

    simulation.finish_game()

    # Determine the winner
    return simulation.get_winner()


def mcts_estimate(game):
    """Perform a Monte Carlo Tree Search to estimate the win probability."""
    start = time.time()

    # Get the unknown cards
    unknown_cards = get_unknown_cards(game)

    # Create a list of all possible opponent hands
    opponent_hands = [list(combo) for combo in itertools.combinations(unknown_cards, 2)]

    # Shuffle to ensure randomness
    random.shuffle(opponent_hands)

    nodes = [LeafNode() for _ in opponent_hands]

    total_playouts = 0

    # Run for 10 seconds
    while time.time() - start < 10:
        # SELECTION
        node = max(nodes, key=lambda n: n.ucb1(total_playouts))
        hand_idx = nodes.index(node)

        # ROLLOUT
        winner = rollout(game, opponent_hands[hand_idx])

        # BACKPROPAGATION
        node.playouts += 1
        total_playouts += 1
        if winner == 1:
            node.wins += 1
        elif winner == 0:  # Tie: count as half win
            node.wins += 0.5

    # After running for 10s, calculate the win probability
    return sum(node.wins for node in nodes) / total_playouts, total_playouts

def continue_game(game):
    """Continue the game by dealing the next set of cards and running MCTS. Prints the state of the game and bot."""
    game.enter_next_phase()
    print("Bot's hand:", game.get_player_1_hand())
    print("Community cards:", game.get_community_cards())
    print("Running MCTS for 10s...")
    win_prob, sims = mcts_estimate(game)
    print(f"Estimated win probability with {sims} simulations: {win_prob:.2%}")
    if win_prob >= 0.5:
        print("Decision: Stay (probability is greater than 50%)")
        return True
    else:
        print("Decision: Fold (probability is less than 50%)")
        return False

def main():
    loop = True
    while loop:
        game = Poker()
        game.start_new_game()

        # Pre-flop
        print("--- PRE-FLOP ---")
        if not continue_game(game):
            print("Bot folds pre-flop.")
            loop = input("Try another game (y/n)?\n").lower() == "y"
            continue

        # Flop
        print("--- FLOP ---")
        if not continue_game(game):
            print("Bot folds on the flop.")
            loop = input("Try another game (y/n)?\n").lower() == "y"
            continue

        # Turn
        print("--- TURN ---")
        if not continue_game(game):
            print("Bot folds on the turn.")
            loop = input("Try another game (y/n)?\n").lower() == "y"
            continue

        # River
        print("--- RIVER & REVEAL ---")
        game.enter_next_phase()
        print("Bot's hand:", game.get_player_1_hand())
        print("Community cards:", game.get_community_cards())
        print("-----------")
        print("Opponent's hand:", game.get_player_2_hand())

        if game.get_winner() == 0:
            print("It's a tie!")
        elif game.get_winner() == 1:
            print("Bot wins!")
        else:
            print("Opponent wins!")

        loop = input("Try another game (y/n)?\n").lower() == "y"
        continue



if __name__ == "__main__":
    main()