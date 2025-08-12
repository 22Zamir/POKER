from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import monte_carlo_strategy
from ai.basic_strategy import simple_strategy, monte_carlo_strategy
from poker.simulator import Player, PokerSimulator

players = [
    Player("Bot1", strategy=simple_strategy),
    Player("Bot2", strategy=monte_carlo_strategy),
    Player("Bot3", strategy=simple_strategy),
]

sim = PokerSimulator(players, big_blind=20)

for i in range(5):
    print(f"\n--- Раздача {i+1} ---")
    sim.play_hand(verbose=True)