from casino.games.blackjack.base import *
from casino.games.blackjack.variants.standard import *
from casino.game_types import *

#Add more tests as needed, potentially testing user inputs
def test_aces():
    """
    Tests extreme cases for having aces in your hand to ensure calculation is correct
    """
    hand = Hand()
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    assert(hand.total == 12)
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    hand.cards[0].rank = 6
    assert(hand.total == 18)
    hand.cards.pop(1)
    assert(hand.total == 17)
    hand.cards[0].rank = 'A'
    total = 12
    while total < 21:
        hand.cards.append(StandardCard(suit="hearts", rank="A"))
        total += 1
        assert(hand.total == total)
    while len(hand.cards) > 3:
        hand.cards.pop()
    hand.cards[0].rank = 10
    hand.cards[1].rank = 10
    assert(hand.total == 21)
    hand.cards.pop(0)
    assert(hand.total == 21)

def test_bust():
    """
    tests scenarios in which the dealer or player busts
    """
    ctx = GameContext(account=Account.generate('test', 100),config=Config.default())
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    #First test case where the player busts and loses
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    blackjack.dealer_hand = Hand()
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts", rank="9"))
    #Add cards to the player's hand to ensure that they lose
    while player_hand.total <= 21:
        player_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.check_win()
    assert(player_hand.result_key == 'player_bust')
    assert('BUSTED' in player_hand.outcome_msg)

    #Next case: Dealer busts and loses
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    blackjack.dealer_hand = Hand()
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="9"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    while blackjack.dealer_hand.total <= 21:
        blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.check_win()
    assert(player_hand.result_key == 'dealer_bust')
    assert('BUSTED' in player_hand.outcome_msg)

    #Next case: Player has 10-10-A and Dealer busts
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    blackjack.dealer_hand = Hand()
    player_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    blackjack.check_win()
    assert(player_hand.result_key == 'dealer_bust')
    assert('BUSTED' in player_hand.outcome_msg)
    #We will test the payout in this scenario as well
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == (balance+player_hand.bet*2))

def test_payout():
    """
    Tests the changes in the user's account for every standard scenario
    Normal win: profit = amount bet
    Push: profit = 0
    Loss: profit = -bet
    """
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    #Case 1: the player beats the dealer normally
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts",rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="9"))
    #Make sure the win result is correct
    blackjack.check_win()
    assert(player_hand.result_key == 'player_wins')
    assert(not player_hand.is_blackjack and not dealer_hand.is_blackjack)
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    #Should be balance before payout + bet*2 because you get back the original money you bet plus the profit
    assert(player.account.balance == (balance+player_hand.bet*2))

    #Case 2: the dealer beats the player normally
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="9"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="2"))
    #Make sure the win result is correct
    blackjack.check_win()
    assert(player_hand.result_key == 'dealer_wins')
    assert(not player_hand.is_blackjack and not dealer_hand.is_blackjack)
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    #Balance should be the same as before because you lost the amount you bet already
    assert(player.account.balance == balance)

    #Case 3: Ties
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    #Make sure the win result is correct
    blackjack.check_win()
    assert(player_hand.result_key == 'tie')
    assert(not player_hand.is_blackjack and not dealer_hand.is_blackjack)
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    #Balance should be higher by the amount bet since it is returned in the case of a tie
    assert(player.account.balance == (balance+player_hand.bet))

def test_blackjack_payout():
    """
    Tests the wins/payouts for every blackjack scenario
    Both get blackjack round 1: Tie
    Player gets blackjack and dealer does not: Blackjack win (profit = 1.5*amount bet)
    Player gets blackjack round 1 and dealer has 21 in round 2: Blackjack win
    Player gets 21 in round 2 and dealer has blackjack: Loss
    Both player and dealer have 21 but neither have blackjack: Tie
    """
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    #Case 1: Both the dealer and the player get blackjack
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    #Make sure the win result is correct
    blackjack.blackjack_check()
    assert player_hand.is_blackjack and dealer_hand.is_blackjack
    blackjack.check_win()
    assert(player_hand.result_key == 'blackjack_tie')
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == (balance+player_hand.bet))

    #Case 2: The player gets blackjack and the dealer does not
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    #Make sure the results are correct
    blackjack.blackjack_check()
    assert(player_hand.is_blackjack and not dealer_hand.is_blackjack)
    blackjack.check_win()
    assert(player_hand.result_key == 'player_blackjack')
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == (balance+player_hand.bet*(1+BLACKJACK_MULTIPLIER)))

    #Case 3: Player has blackjack, dealer 21 with more than 2 cards
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    blackjack.blackjack_check()
    assert player_hand.is_blackjack and not dealer_hand.is_blackjack
    blackjack.check_win()
    assert(player_hand.result_key == 'player_blackjack')
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == (balance+player_hand.bet*(1+BLACKJACK_MULTIPLIER)))

    #Case 4: Both dealer and player have 21 but more than 2 cards
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="10"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    blackjack.blackjack_check()
    assert not(player_hand.is_blackjack or dealer_hand.is_blackjack)
    blackjack.check_win()
    assert(player_hand.result_key == 'tie')
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == (balance+player_hand.bet))

    #Case 5: Player has 21 but dealer has blackjack
    player_hand = Hand(bet=10)
    player.hands = [player_hand]
    dealer_hand = Hand()
    blackjack.dealer_hand = dealer_hand
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="K"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="A"))
    dealer_hand.cards.append(StandardCard(suit="hearts", rank="Q"))
    blackjack.blackjack_check()
    assert not player_hand.is_blackjack and dealer_hand.is_blackjack
    blackjack.check_win()
    assert(player_hand.result_key == 'dealer_blackjack')
    #Test the payout
    balance = player.account.balance
    blackjack.payout()
    assert(player.account.balance == balance)

def test_dealer_decision():
    """
    Tests the dealer's decisions in certain situations
    Dealer total is less than or equal to 16: Hit
    Dealer total is greater than or equal to 17: Stand
    Edge case: Dealer stands on Ace + 6
    """
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    blackjack = StandardBlackjack(ctx)

    player_hand = Hand()
    blackjack.player.hands = [player_hand]
    player_hand.cards.append(StandardCard(suit="hearts", rank="2"))
    player_hand.cards.append(StandardCard(suit="hearts", rank="3"))

    dealer = blackjack.dealer_hand
    dealer.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer.cards.append(StandardCard(suit="hearts", rank=8))
    blackjack.dealer_draw()
    assert(len(dealer.cards) == 2)

    dealer.cards[1].rank = 6
    blackjack.dealer_draw()
    assert(len(dealer.cards) == 3)

    dealer.cards.pop()
    dealer.cards[0].rank = 'A'
    blackjack.dealer_draw()
    assert(len(dealer.cards) == 2)