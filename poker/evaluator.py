"""
Оценка покерной руки (Texas Hold'em style).

Основная функция:
- evaluate_best_hand(cards: List[Card]) -> (rank_category, tiebreaker_tuple)

Возвращает:
- category: int (8 = straight flush, 7 = four of a kind, 6 = full house, 5 = flush,
                    4 = straight, 3 = three of a kind, 2 = two pair, 1 = one pair, 0 = high card)
- tiebreaker_tuple: tuple[int,...] — используется для сравнения рук одинаковой категории.

Интерфейс принимает 2..7 карт (Card объекты).
Алгоритм: перебор всех 5-картных комбинаций (itertools.combinations) -> нахождение лучшей.
(Для прототипа достаточно и прозрачно; для скорости в продакшн можно подменять на C-алгоритм)
"""

from itertools import combinations
from typing import List, Tuple
from collections import Counter

from .cards import Card

# Категории по убыванию силы:
CATEGORY_NAMES = {
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card",
}


def _is_flush(cards: List[Card]) -> bool:
    suits = [c.suit for c in cards]
    return len(set(suits)) == 1


def _is_straight(ranks: List[int]) -> Tuple[bool, int]:
    """
    ranks: list of ranks sorted desc unique (e.g. [14,13,12,11,10])
    Return (is_straight, high_card_rank)
    Handles wheel (A-2-3-4-5) -> high_card_rank = 5
    """
    # unique sorted descending
    uniq = sorted(set(ranks), reverse=True)
    # handle wheel: treat Ace as 1
    if len(uniq) < 5:
        return (False, 0)
    # Try all consecutive windows of length 5
    for i in range(len(uniq) - 4):
        window = uniq[i:i + 5]
        # check consecutive
        if window[0] - window[4] == 4 and all(window[j] - window[j + 1] == 1 for j in range(4)):
            return (True, window[0])
    # check wheel specifically (A,5,4,3,2)
    if set([14, 5, 4, 3, 2]).issubset(set(ranks)):
        return (True, 5)
    return (False, 0)


def _classify_five(cards: List[Card]) -> Tuple[int, Tuple]:
    """
    Оценка ровно 5 карт — возвращает (category, tiebreaker_tuple).
    tiebreaker_tuple должен сравниваться лексикографически: больше лучше.
    """
    ranks = [c.rank for c in cards]
    ranks_sorted_desc = sorted(ranks, reverse=True)
    counts = Counter(ranks)
    counts_by_rank = sorted(((cnt, rank) for rank, cnt in counts.items()), reverse=True)
    # counts_by_rank: sorted by (count desc, rank desc)
    # e.g. four of a kind -> [(4, 9),(1,14)] if four 9s + ace kicker

    is_flush = _is_flush(cards)
    is_straight, straight_high = _is_straight(ranks)

    # Straight flush
    if is_flush and is_straight:
        return (8, (straight_high,))

    # Four of a kind
    if counts_by_rank[0][0] == 4:
        four_rank = counts_by_rank[0][1]
        kicker = max(r for r in ranks if r != four_rank)
        return (7, (four_rank, kicker))

    # Full house (3 + 2)
    if counts_by_rank[0][0] == 3 and any(cnt == 2 for cnt, _ in counts_by_rank[1:]):
        three_rank = counts_by_rank[0][1]
        pair_rank = max(r for cnt, r in counts_by_rank[1:] if cnt == 2)
        return (6, (three_rank, pair_rank))

    # Three-of-a-kind but maybe with two singles -> Need to ensure not full house (already handled)
    # Flush
    if is_flush:
        return (5, tuple(ranks_sorted_desc))

    # Straight
    if is_straight:
        return (4, (straight_high,))

    # Three of a kind
    if counts_by_rank[0][0] == 3:
        three_rank = counts_by_rank[0][1]
        kickers = sorted((r for r in ranks if r != three_rank), reverse=True)
        return (3, (three_rank, kickers[0], kickers[1]))

    # Two pair
    if counts_by_rank[0][0] == 2 and counts_by_rank[1][0] == 2:
        high_pair = counts_by_rank[0][1]
        low_pair = counts_by_rank[1][1]
        kicker = max(r for r in ranks if r != high_pair and r != low_pair)
        return (2, (high_pair, low_pair, kicker))

    # One pair
    if counts_by_rank[0][0] == 2:
        pair_rank = counts_by_rank[0][1]
        kickers = sorted((r for r in ranks if r != pair_rank), reverse=True)
        return (1, (pair_rank, kickers[0], kickers[1], kickers[2]))

    # High card
    return (0, tuple(ranks_sorted_desc))


def evaluate_best_hand(cards: List[Card]) -> Tuple[int, Tuple]:
    """
    Принимает список из 2..7 карт. Перебирает все 5-картные комбинации и возвращает
    лучшую найденную пару (category, tiebreaker_tuple).
    """
    if not (2 <= len(cards) <= 7):
        raise ValueError("cards must be a list of length between 2 and 7")
    best = (-1, ())
    for combo in combinations(cards, 5):
        cat, tie = _classify_five(list(combo))
        # сравниваем сначала по категории, затем по tiebreaker
        if (cat, tie) > best:
            best = (cat, tie)
    return best


def hand_rank_string(rank_tuple: Tuple[int, Tuple]) -> str:
    cat, tie = rank_tuple
    name = CATEGORY_NAMES.get(cat, f"Unknown({cat})")
    return f"{name} {tie}"

# Пример использования:
# >>> from poker.cards import parse_card
# >>> from poker.evaluator import evaluate_best_hand, hand_rank_string
# >>> cards = [parse_card(x) for x in ('As','Ks','Qs','Js','Ts','2d','3c')]
# >>> rank = evaluate_best_hand(cards)
# >>> print(hand_rank_string(rank))  # Straight Flush (A high)
