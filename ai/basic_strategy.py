"""
Базовая стратегия для покерного бота:
- Использует Монте-Карло симуляции, чтобы оценить шанс победы.
- Решение: fold / call / allin по порогам win_rate.

Вызов:
    action = monte_carlo_strategy(player, community_cards, pot)
"""

import random
from typing import List
from poker.cards import Deck, Card
from poker.evaluator import evaluate_best_hand


def simple_strategy(player, community_cards, pot, stage):
    """
    Очень простая стратегия:
    - На Preflop: коллим, если пара или карта старше десятки, иначе фолд
    - На остальных стадиях всегда коллим
    """
    ranks = [card.rank for card in player.hand]

    if stage == "Preflop":
        if ranks[0] == ranks[1] or any(r >= 10 for r in ranks):
            return "call"
        else:
            return "fold"
    else:
        return "call"


def estimate_win_rate(player_cards: List[Card],
                      community_cards: List[Card],
                      num_opponents: int,
                      num_simulations: int = 500,
                      rng=None) -> float:
    """
    Оценивает вероятность победы методом Монте-Карло.
    Возвращает win_rate (0.0..1.0).
    """
    rng = rng or random.Random()
    wins = 0
    ties = 0

    known_cards = player_cards + community_cards
    for _ in range(num_simulations):
        # Создаём колоду без известных карт
        deck = Deck(rng)
        deck.cards = [c for c in deck.cards if c not in known_cards]
        deck.shuffle()

        # Достраиваем борд
        missing_board = 5 - len(community_cards)
        sim_board = community_cards + deck.deal(missing_board)

        # Раздаём соперникам
        opponents_hands = [deck.deal(2) for _ in range(num_opponents)]

        # Оценка всех рук
        my_rank = evaluate_best_hand(player_cards + sim_board)
        opp_ranks = [evaluate_best_hand(hand + sim_board) for hand in opponents_hands]

        # Сравнение
        best_rank = max([my_rank] + opp_ranks)
        if my_rank == best_rank:
            if opp_ranks.count(best_rank) == 0:
                wins += 1
            else:
                # Если есть ещё такие же сильные руки — ничья
                if my_rank in opp_ranks:
                    ties += 1

    return (wins + ties * 0.5) / num_simulations


def monte_carlo_strategy(player, community_cards, pot, stage):
    """
    Стратегия с разным поведением по стадиям.
    Пока простой пример:
    - На Preflop играем осторожно
    - На остальных стадиях считаем win_rate и принимаем решение
    """
    if stage == "Preflop":
        ranks = [card.rank for card in player.hand]
        if ranks[0] == ranks[1] or any(r >= 10 for r in ranks):
            return "call"
        else:
            return "fold"
    else:
        win_rate = estimate_win_rate(
            player.hand,
            community_cards,
            num_opponents=sum(
                1 for p in player.simulator.players if p.in_game and p != player),
        )
        if win_rate > 0.7:
            return "allin"
        elif win_rate > 0.4:
            return "call"
        else:
            return "fold"
