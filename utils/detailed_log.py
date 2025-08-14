import os
from datetime import datetime
from typing import List
from poker.cards import Card


class PokerLogger:
    def __init__(self, log_file="poker_game.log"):
        self.log_file = log_file
        self.last_action = None    # 'bluff_raise', 'raise', 'fold' и т.д.
        self.last_player = None    # кто последним сделал действие
        self._clear_log()

    def log_bluff_raise(self, player_name: str, amount: int, pot: int):
        self._write(f"  {player_name} → 🎭 BLUFF RAISE {amount}! (банк: {pot})")
        self.last_action = 'bluff_raise'
        self.last_player = player_name

    def log_call(self, player_name: str, amount: int, pot: int):
        self._write(f"  {player_name} → CALL {amount} (банк: {pot})")
        self.last_action = 'call'
        self.last_player = player_name

    def log_fold(self, player_name: str, pot: int):
        self._write(f"  {player_name} → FOLD (банк: {pot})")
        self.last_action = 'fold'
        self.last_player = player_name

    def _clear_log(self):
        """Очищаем файл перед новой сессией"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"--- Новая сессия: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")

    def log_hand_start(self, hand_num: int):
        self._write(f"\n--- Раздача {hand_num} ---")

    def log_preflop(self, players: List):
        self._write("[Preflop] Карты розданы:")
        for p in players:
            if p.in_game:
                hand_str = " ".join(c.pretty() for c in p.hand)
                self._write(f"  {p.name}: {hand_str} (стек: {p.stack})")

    def log_board(self, stage: str, board: List[Card]):
        board_str = " ".join(c.pretty() for c in board)
        self._write(f"[{stage}] Борд: {board_str}")

    def log_action(self, player_name: str, action: str, pot: int):
        self._write(f"  {player_name} → {action.upper()} (банк: {pot})")

   # def log_fold(self, player_name: str, pot: int):
    #    self._write(f"  {player_name} → FOLD (банк: {pot})")

    #def log_call(self, player_name: str, amount: int, pot: int):
    #    self._write(f"  {player_name} → CALL {amount} (банк: {pot})")

    def log_raise(self, player_name: str, amount: int, pot: int, raise_type: str = "RAISE"):
        self._write(f"  {player_name} → {raise_type} {amount}! (банк: {pot})")

    def log_allin(self, player_name: str, amount: int, pot: int):
        self._write(f"  {player_name} → ALL-IN {amount}! (банк: {pot})")

    def log_showdown(self, winners: List[str], pot: int, best_rank: tuple):
        if winners:
            self._write(f"🏆 Шоудаун: победитель(и): {', '.join(winners)} → +{pot // len(winners)}")
        else:
            self._write(f"🏆 Шоудаун: нет победителей (банк: {pot})")

    def log_all_folded(self, winner: str, pot: int):
        self._write(f"🎉 Все сбросили! {winner} забирает {pot}")

    def log_stacks(self, players: List):
        stacks = " | ".join(f"{p.name}: {p.stack}" for p in players)
        self._write(f"📊 Стеки: {stacks}")

    def _write(self, text: str):
        print(text)  # Вывод в консоль
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def log_bluff_raise(self, player_name: str, amount: int, pot: int):
        self._write(f"  {player_name} → 🎭 BLUFF RAISE {amount}! (банк: {pot})")
