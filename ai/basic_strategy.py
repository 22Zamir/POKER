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


def simple_strategy(player, community_cards, pot, stage, current_bet=None):
    """
    Очень простая стратегия:
    - На Preflop: коллим, если пара или карта старше десятки, иначе фолд
    - На остальных стадиях:
        - Коллим, если ставка меньше половины стека
        - Фолд, если ставка больше половины стека
    """
    ranks = [card.rank for card in player.hand]

    if stage == "Preflop":
        if ranks[0] == ranks[1] or any(r >= 10 for r in ranks):
            return "call"
        else:
            return "fold"
    else:
        # На других стадиях проверяем размер ставки
        if current_bet is None:
            current_bet = player.simulator.bb  # По умолчанию big blind

        # Если ставка больше половины стека — фолд
        if current_bet > player.stack / 2:
            return "fold"
        else:
            return "call"


def aggressive_strategy(player, community_cards, pot, stage):
    """
    Умная стратегия:
    - Использует позицию
    - Делает рейзы в поздней позиции
    - Иногда блефует
    - Оценивает win_rate
    """
    # Оцениваем шансы
    num_opponents = sum(1 for p in player.simulator.players if p.in_game and p != player)
    win_rate = estimate_win_rate(
        player.hand,
        community_cards,
        num_opponents=num_opponents,
        num_simulations=300
    )

    is_late_position = player.position in ["CO", "BTN"]
    is_mid_position = player.position in ["MP", "UTG"]
    pot_odds = pot / (pot + 20)  # шанс окупить колл

    if stage == "Preflop":
        ranks = [c.rank for c in player.hand]
        suited = player.hand[0].suit == player.hand[1].suit
        connected = abs(ranks[0] - ranks[1]) == 1

        # Поздняя позиция — агрессивнее
        if is_late_position:
            if ranks[0] == ranks[1] or any(r >= 11 for r in ranks):  # пара или J+
                return "raise_2x"
            elif suited and connected:
                return "call"
            else:
                return "fold"
        else:
            if ranks[0] == ranks[1]:
                return "raise_2x"
            elif any(r >= 13 for r in ranks):  # K, A
                return "call"
            else:
                return "fold"

    else:
        # Постфлоп
        if win_rate > 0.7:
            return "raise_pot"
        elif win_rate > 0.5:
            return "raise_2x"
        elif win_rate > 0.3:
            if is_late_position and random.random() < 0.4:
                return "bluff_raise_2x"  # Блеф в 40% случаев
            elif random.random() < 0.7:
                return "call"
            else:
                return "fold"
        else:
            return "fold"


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


def monte_carlo_strategy(player, community_cards, pot, stage, current_bet=None):
    """
    Улучшенная стратегия с рейзами на основе win_rate.
    """
    num_opponents = sum(
        1 for p in player.simulator.players if p.in_game and p != player
    )
    win_rate = estimate_win_rate(
        player.hand,
        community_cards,
        num_opponents=num_opponents,
        num_simulations=300
    )

    if stage == "Preflop":
        ranks = [card.rank for card in player.hand]
        if ranks[0] == ranks[1]:
            return "raise_2x"
        elif any(r >= 12 for r in ranks):  # Q, K, A
            return "raise_2x"
        elif any(r >= 10 for r in ranks):
            return "call"
        else:
            return "fold"
    else:
        if win_rate > 0.8:
            return "raise_pot"
        elif win_rate > 0.6:
            return "raise_2x"
        elif win_rate > 0.4:
            return "call"
        else:
            return "fold"
