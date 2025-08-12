"""
Минимальный симулятор Texas Hold'em для тестирования бота.

⚠ Упрощения:
- Нет сложной экономики ставок, только фиксированные блайнды и "колл/фолд".
- Нет разделения банка, сайд-потов.
- Все игроки, кроме фолдовших, доходят до вскрытия.
- Работает с объектами Card из poker/cards.py и функцией evaluate_best_hand из poker/evaluator.py.

Цель: дать среду, где можно тренировать или тестировать стратегии.
"""

import random
from typing import List, Callable

from .cards import Deck, Card
from .evaluator import evaluate_best_hand

class Player:
    def __init__(self, name: str, strategy: Callable, stack: int = 1000):
        self.name = name
        self.strategy = strategy
        self.stack = stack
        self.hand: List[Card] = []
        self.in_game = True  # не сбросил карты
        self.simulator = None  # ссылка на симулятор, установится в PokerSimulator

    def reset_for_new_hand(self):
        self.hand.clear()
        # Игрок в игре только если есть стек
        self.in_game = self.stack > 0

class PokerSimulator:
    def __init__(self, players: List[Player], big_blind: int = 20, rng=None):
        if len(players) < 2:
            raise ValueError("Нужно хотя бы 2 игрока")
        self.players = players
        self.bb = big_blind
        self.rng = rng or random.Random()

        for p in players:
            p.simulator = self

    def play_hand(self, verbose=True):
        self.deck = Deck(self.rng)
        self.deck.shuffle()
        self.pot = 0

        # Сброс рук и статуса игроков
        for p in self.players:
            p.reset_for_new_hand()

        # Раздача по 2 карты каждому игроку
        for p in self.players:
            p.hand = self.deck.deal(2)

        stages = ["Preflop", "Flop", "Turn", "River"]
        community_cards = []

        for stage in stages:
            if stage != "Preflop":
                cards_to_add = {"Flop": 3, "Turn": 1, "River": 1}[stage]
                community_cards += self.deck.deal(cards_to_add)

            if verbose:
                print(f"\n[{stage}] Борд: {' '.join(str(c) for c in community_cards)}")

            for player in self.players:
                # Игрок ходит только если в игре и есть стек
                if player.in_game and player.stack > 0:
                    action = player.strategy(player, community_cards, self.pot, stage)
                    if verbose:
                        print(f"{player.name} -> {action}")

                    if action == "fold":
                        player.in_game = False
                    elif action == "call":
                        call_amount = self.bb  # упрощаем, можно улучшить
                        bet = min(call_amount, player.stack)
                        player.stack -= bet
                        self.pot += bet
                        # Если стек закончился, игрок выбывает
                        if player.stack == 0:
                            player.in_game = False
                    elif action == "allin":
                        bet = player.stack
                        player.stack = 0
                        self.pot += bet
                        player.in_game = False  # all-in означает больше нет ходов

            if verbose:
                for p in self.players:
                    print(f"{p.name} стек: {p.stack}")

            # Проверяем сколько осталось активных игроков с деньгами
            active = [p for p in self.players if p.in_game and p.stack > 0]
            if len(active) == 1:
                winner = active[0]
                winner.stack += self.pot
                if verbose:
                    print(f"\nВсе сбросили, {winner.name} забрал {self.pot}")
                return {
                    "winners": [winner.name],
                    "pot": self.pot,
                    "rank": None
                }

        # Если дошли до шоудауна - определяем победителя
        best_rank = None
        winners = []
        for p in self.players:
            if not p.in_game:
                continue
            rank = evaluate_best_hand(p.hand + community_cards)
            if best_rank is None or rank > best_rank:
                best_rank = rank
                winners = [p]
            elif rank == best_rank:
                winners.append(p)

        if not winners:
            # Никто не остался для шоудауна — просто вернуть информацию без деления
            if verbose:
                print("\nНикто не остался для шоудауна, банк не распределён.")
            return {
                "winners": [],
                "pot": self.pot,
                "rank": None
            }

        split_pot = self.pot // len(winners)
        for w in winners:
            w.stack += split_pot

        if verbose:
            print(f"\nПобедитель(и): {[w.name for w in winners]} получили {split_pot} каждый")

        return {
            "winners": [w.name for w in winners],
            "pot": self.pot,
            "rank": best_rank
        }
