import itertools
import random

SCORE_HIGH_CARD = 1
SCORE_ONE_PAIR = 2
SCORE_TWO_PAIR = 3
SCORE_THREE_OF_A_KIND = 4
SCORE_STRAIGHT = 5
SCORE_FLUSH = 6
SCORE_FULL_HOUSE = 7
SCORE_FOUR_OF_A_KIND = 8
SCORE_STRAIGHT_FLUSH = 9
RANK_TO_VAL = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "Jack": 11,
    "Queen": 12,
    "King": 13,
    "Ace": 14
}

class Poker:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        self.id_to_card = [(rank, suit) for suit in suits for rank in ranks]

        self.deck = None
        self.player_1_hand = []
        self.player_2_hand = []
        self.community_cards = []
        self.phase = 0

    def copy_with_random_state(self):
        """Returns a copy of the game with a random unobservable state. Leaves player 2's hand empty."""
        # Copy everything observable
        new_game = Poker()
        new_game.id_to_card = self.id_to_card
        new_game.player_1_hand = self.player_1_hand.copy()
        new_game.community_cards = self.community_cards.copy()
        new_game.phase = self.phase

        # Set random unobservable state by reinitializing the deck
        new_game.deck = [i for i in range(52)]

        # Remove cards already dealt
        for card in new_game.player_1_hand + new_game.community_cards:
            new_game.deck.remove(card)

        # Shuffle the deck
        random.shuffle(new_game.deck)

        return new_game

    def _id_to_rank(self, id):
        """Returns the rank of a card from its ID."""
        return RANK_TO_VAL[self.id_to_card[id][0]]

    def _deal_hole_cards(self):
        """Deals 2 hole cards to each player."""
        for i in range(2):
            self.player_1_hand.append(self.deck.pop())
            self.player_2_hand.append(self.deck.pop())

    def _deal_new_community_cards(self, num_cards):
        """Deals the specified number of community cards."""
        for i in range(num_cards):
            self.community_cards.append(self.deck.pop())
        
    def start_new_game(self):
        """Resets the game to a new state."""
        self.deck = [i for i in range(52)]
        self.shuffle_deck()
        self.phase = 0

        self.player_1_hand = []
        self.player_2_hand = []
        self.community_cards = []
        
    def card_name(self, id):
        """Returns the name of the card of an ID in the deck."""
        return f"{self.id_to_card[id][0]} of {self.id_to_card[id][1]}"

    def shuffle_deck(self):
        """Shuffles the current unplayed deck of cards."""
        random.shuffle(self.deck)
        
    def enter_next_phase(self):
        """Deals the next set of cards based on the current phase."""
        if self.phase == 0:
            self._deal_hole_cards()
        elif self.phase == 1:
            self._deal_new_community_cards(3) # Flop
        elif 2 <= self.phase <= 3:
            self._deal_new_community_cards(1) # Turn or River
        else:
            raise ValueError("Game has already ended.")

        self.phase += 1

    def finish_game(self):
        """Continues the game until the end."""
        while self.phase <= 3:
            self.enter_next_phase()

    def get_player_1_hand(self):
        """Returns player 1"s hand as a list of formatted strings."""
        return [self.card_name(card) for card in self.player_1_hand]

    def get_player_2_hand(self):
        """Returns player 2"s hand as a list of formatted strings."""
        return [self.card_name(card) for card in self.player_2_hand]

    def get_community_cards(self):
        """Returns the community cards as a list of formatted strings."""
        return [self.card_name(card) for card in self.community_cards]

    def _check_flush(self, hand):
        """Return 1 if flush exists, otherwise 0."""
        suits = [self.id_to_card[card][1] for card in hand]
        suits_set = set(suits)

        if len(suits_set) == 1:
            return 1
        else:
            return 0

    @staticmethod
    def _check_straight(player_sorted_ranks):
        """Return the rank of the highest card in the straight if it exists, otherwise 0."""
        # Check for a straight
        if (player_sorted_ranks[1] == player_sorted_ranks[0] + 1 and
            player_sorted_ranks[2] == player_sorted_ranks[0] + 2 and
            player_sorted_ranks[3] == player_sorted_ranks[0] + 3 and
            player_sorted_ranks[4] == player_sorted_ranks[0] + 4):
            return player_sorted_ranks[4]

        # Check for Ace, 2, 3, 4, 5 straight (lowest ranking straight)
        if (player_sorted_ranks[0] == 2 and
            player_sorted_ranks[1] == 3 and
            player_sorted_ranks[2] == 4 and
            player_sorted_ranks[3] == 5 and
            player_sorted_ranks[4] == 14):
            return 5

        return 0

    @staticmethod
    def _rank_counts(player_sorted_ranks):
        """Returns a list of lists of the form [[count, rank],] sorted by count, then rank."""
        rank_count = {}
        for rank in player_sorted_ranks:
            if rank in rank_count:
                rank_count[rank] += 1
            else:
                rank_count[rank] = 1

        rank_count = [[count, rank] for rank, count in rank_count.items()]
        rank_count.sort(reverse=True)  # sort by count, then by rank
        return rank_count

    def _evaluate_combination(self, cards):
        """Returns the score of a 5-card hand and kickers (in a list) in a tuple of length 2."""
        sorted_ranks = sorted([self._id_to_rank(card) for card in cards])

        rank_counts = self._rank_counts(sorted_ranks)


        flush = self._check_flush(cards)
        straight = self._check_straight(sorted_ranks)

        # Straight flush
        if flush and straight:
            return SCORE_STRAIGHT_FLUSH, [straight]

        # Four of a kind
        if rank_counts[0][0] == 4:
            kicker = rank_counts[1][1]
            return SCORE_FOUR_OF_A_KIND, [rank_counts[0][1], kicker]

        # Full house
        if rank_counts[0][0] == 3 and rank_counts[1][0] == 2:
            return SCORE_FULL_HOUSE, [rank_counts[0][1], rank_counts[1][1]]

        # Flush
        if flush:
            sorted_ranks.reverse()
            return SCORE_FLUSH, sorted_ranks

        # Straight
        if straight:
            return SCORE_STRAIGHT, [straight]

        # Three of a kind
        if rank_counts[0][0] == 3:
            kickers = []
            for i in range(1, len(rank_counts)):
                kickers.append(rank_counts[i][1])
            return SCORE_THREE_OF_A_KIND, [rank_counts[0][1]] + kickers

        # Two pair
        if rank_counts[0][0] == 2 and rank_counts[1][0] == 2:
            return SCORE_TWO_PAIR, [rank_counts[0][1]] + [rank_counts[1][1]] + [rank_counts[2][1]]

        # One pair
        if rank_counts[0][0] == 2:
            kickers = []
            for i in range(1, len(rank_counts)):
                kickers.append(rank_counts[i][1])
            return SCORE_ONE_PAIR, [rank_counts[0][1]] + kickers

        # High card
        sorted_ranks.reverse()
        return SCORE_HIGH_CARD, sorted_ranks

    def _best_score(self, player_cards):
        """Returns the best score tuple of a 5-card hand from the player's cards."""
        best = None
        # Generate all combinations of 5 cards from the player's hand and community cards
        for combo in itertools.combinations(player_cards, 5):
            candidate = self._evaluate_combination(combo)
            if best is None or candidate > best:
                best = candidate
        return best

    def get_winner(self):
        """Returns the winner of the game. 0 for tie."""
        if self.phase < 4:
            raise ValueError("Game is not over yet.")

        p1_cards = self.player_1_hand + self.community_cards
        p2_cards = self.player_2_hand + self.community_cards

        p1_score = self._best_score(p1_cards)
        p2_score = self._best_score(p2_cards)

        if p1_score > p2_score:
            return 1
        elif p2_score > p1_score:
            return 2
        else:
            return 0 # Tie
