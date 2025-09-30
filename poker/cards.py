"""
Карты и колода для покера.

Основные типы:
- Card : объект карты (rank, suit)
- Deck : стандартная колода на 52 карты, умеет тасовать и сдавать
- helpers: parse_card (строка -> Card), card_str (Card -> строка)

Формат строковых карт: 'As' = туз пик, 'Td' = десятка бубен, '2c' = двойка треф и т.д.
Ranks: 2-9, T, J, Q, K, A
Suits: s (spades), h (hearts), d (diamonds), c (clubs)
"""

from dataclasses import dataclass
import random
from typing import List

RANK_STR_TO_INT = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

INT_TO_RANK_STR = {v: k for k, v in RANK_STR_TO_INT.items()}

SUITS = {'s', 'h', 'd', 'c'}
SUIT_SYMBOLS = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}


@dataclass(frozen=True, order=True)
class Card:
    rank: int  # 2..14
    suit: str  # 's','h','d','c'

    def __post_init__(self):
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit: {self.suit}")
        if not (2 <= self.rank <= 14):
            raise ValueError(f"Invalid rank: {self.rank}")

    def __str__(self) -> str:
        return f"{INT_TO_RANK_STR[self.rank]}{self.suit}"

    def __repr__(self) -> str:
        return f"Card({self.rank}, '{self.suit}')"

    def pretty(self) -> str:
        return f"{INT_TO_RANK_STR[self.rank]}{SUIT_SYMBOLS[self.suit]}"

    def rank_str(self) -> str:
        """Возвращает строковое обозначение ранга: A, K, Q, J, T, 9, ..., 2"""
        return INT_TO_RANK_STR[self.rank]


def parse_card(s: str) -> Card:
    """
    Парсит строку в карту.
    Примеры: 'As', 'Td', '2c'
    """
    if not isinstance(s, str) or len(s) != 2:
        raise ValueError(f"Card string must be 2 chars like 'As', got {s!r}")
    r, suit = s[0].upper(), s[1].lower()
    if r not in RANK_STR_TO_INT:
        raise ValueError(f"Invalid rank symbol: {r!r}")
    if suit not in SUITS:
        raise ValueError(f"Invalid suit: {suit!r}")
    return Card(rank=RANK_STR_TO_INT[r], suit=suit)


def card_from_tuple(tup):
    """Удобство: (rank_int, suit_char) -> Card"""
    r, s = tup
    return Card(rank=int(r), suit=s)


class Deck:
    """Стандартная колода 52 карты."""

    def __init__(self, rng=None):
        self.cards: List[Card] = [Card(rank=r, suit=s) for s in SUITS for r in range(2, 15)]
        self.rng = rng or random.Random()

    def shuffle(self):
        self.rng.shuffle(self.cards)

    def deal(self, n=1) -> List[Card]:
        if n < 1:
            return []
        if n > len(self.cards):
            raise ValueError("Not enough cards to deal")
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def burn(self, n=1):
        self.deal(n)

    def __len__(self):
        return len(self.cards)

# Примеры использования:
# >>> from poker.cards import parse_card, Deck
# >>> parse_card('As')  # A of spades
# >>> d = Deck(); d.shuffle(); d.deal(2)
