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
from utils.detailed_log import PokerLogger
from .cards import Deck, Card
from .evaluator import evaluate_best_hand


class Player:
    def __init__(self, name: str, strategy: Callable, stack: int = 1000, position: str = None):
        self.name = name
        self.strategy = strategy
        self.stack = stack
        self.hand: List[Card] = []
        self.in_game = True
        self.simulator = None
        self.position = position  # например, "BTN", "UTG"

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
        self.community_cards = []
        self.pot = 0
        self.logger = PokerLogger()
        self.hand_counter = 0
        self.deck = None
        self.current_stage = 0
        self.stages = ["Preflop", "Flop", "Turn", "River"]

        for p in players:
            p.simulator = self

    def play_hand(self, verbose=True):
        """Автоматически проходит всю раздачу от начала до конца."""
        self.hand_counter += 1
        self.logger.log_hand_start(self.hand_counter)

        self.start_hand()

        result = None
        for _ in range(4):  # Preflop → Flop → Turn → River
            result = self.next_stage()
            if result["action"] != "continue":
                break

        if verbose:
            if result["action"] == "all_folded":
                self.logger.log_all_folded(result["winner"], result["pot"])
            elif result["action"] == "showdown":
                self.logger.log_showdown(result["winners"], result["pot"], result.get("rank"))
            self.logger.log_stacks(self.players)

        return result

    def start_hand(self):
        """Начинаем новую раздачу."""
        self.deck = Deck(self.rng)
        self.deck.shuffle()
        self.pot = 0
        self.community_cards = []
        self.current_stage = 0

        # Сброс игроков
        for p in self.players:
            p.reset_for_new_hand()

        # Раздача карт
        for p in self.players:
            if p.in_game:
                p.hand = self.deck.deal(2)

    def next_stage(self) -> dict:
        """Переход к следующей стадии: Preflop → Flop → Turn → River → Showdown"""
        if self.current_stage >= len(self.stages):
            return {"error": "Игра завершена"}

        stage = self.stages[self.current_stage]
        self.current_stage += 1

        # Добавляем карты на борд
        if stage == "Flop":
            self.community_cards += self.deck.deal(3)
        elif stage == "Turn":
            self.community_cards += self.deck.deal(1)
        elif stage == "River":
            self.community_cards += self.deck.deal(1)

        # Логика ставок на текущей стадии
        result = self._play_betting_round(stage)

        # Если остался один игрок — он забирает банк
        if "winner" in result:
            return result

        # Если это последняя стадия — определяем победителя
        if stage == "River":
            return self._showdown()

        return {
            "stage": stage,
            "community_cards": self.community_cards,
            "pot": self.pot,
            "action": "continue"
        }

    def _play_betting_round(self, stage: str) -> dict:
        """Обработка действий игроков с поддержкой raise."""
        self.current_bet = self.bb  # Начальная ставка = big blind

        for player in self.players:
            if not (player.in_game and player.stack > 0):
                continue

            action = player.strategy(player, self.community_cards, self.pot, stage)

            if action == "fold":
                player.in_game = False
                self.logger.log_fold(player.name, self.pot)
            elif action == "call":
                bet = min(self.current_bet, player.stack)  # Коллим текущую ставку
                player.stack -= bet
                self.pot += bet
                self.logger.log_call(player.name, bet, self.pot)
                if player.stack == 0:
                    player.in_game = False
            elif action.startswith("raise_"):
                # Поддержка: raise_2x, raise_pot, etc.
                multiplier = action.replace("raise_", "").replace("x", "")
                if multiplier == "pot":
                    bet = min(self.pot, player.stack)
                elif multiplier == "half":
                    bet = min(self.pot // 2, player.stack)
                else:
                    try:
                        mult = float(multiplier)
                        bet = min(int(self.current_bet * mult), player.stack)
                    except:
                        bet = min(self.current_bet, player.stack)  # fallback

                self.logger.log_bluff_raise(player.name, bet, self.pot)
                player.stack -= bet
                self.pot += bet
                self.current_bet = bet  # Обновляем текущую ставку
                self.logger.log_action(player.name, f"RAISE {bet}", self.pot)
                if player.stack == 0:
                    player.in_game = False
            elif action == "allin":
                bet = player.stack
                player.stack = 0
                self.pot += bet
                self.logger.log_allin(player.name, bet, self.pot)
            elif action.startswith("bluff_raise"):
                # То же, что обычный raise, но с пометкой
                base_action = action.replace("bluff_", "")
                # Просто обрабатываем как обычный raise
                multiplier = base_action.replace("raise_", "").replace("x", "")
                if multiplier == "pot":
                    bet = min(self.pot, player.stack)
                else:
                    try:
                        mult = float(multiplier)
                        bet = min(int(self.bb * mult), player.stack)
                    except:
                        bet = min(self.bb, player.stack)
                player.stack -= bet
                self.pot += bet
                self.current_bet = bet
                self.logger.log_action(player.name, f"BLUFF RAISE {bet}!", self.pot)
                if player.stack == 0:
                    player.in_game = False

        # Проверка: остался ли один активный игрок?
        active = [p for p in self.players if p.in_game and p.stack > 0]
        if len(active) == 1:
            winner = active[0]
            winner.stack += self.pot
            return {
                "winner": winner.name,
                "pot": self.pot,
                "action": "all_folded"
            }

        return {"action": "continue"}

    def _showdown(self) -> dict:
        """Определение победителя по силе руки."""
        best_rank = None
        winners = []
        for p in self.players:
            if not p.in_game:
                continue
            rank = evaluate_best_hand(p.hand + self.community_cards)
            if best_rank is None or rank > best_rank:
                best_rank = rank
                winners = [p]
            elif rank == best_rank:
                winners.append(p)

        # Даже если победителей нет — возвращаем action
        if not winners:
            return {
                "winners": [],
                "pot": self.pot,
                "rank": None,
                "action": "showdown"
            }

        split_pot = self.pot // len(winners)
        for w in winners:
            w.stack += split_pot

        return {
            "winners": [w.name for w in winners],
            "pot": self.pot,
            "rank": best_rank,
            "action": "showdown"
        }
