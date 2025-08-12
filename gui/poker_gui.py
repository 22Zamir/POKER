import tkinter as tk
from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import simple_strategy

# gui/poker_gui.py

import tkinter as tk
from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import simple_strategy


class PokerGUI(tk.Tk):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.title("Poker Simulator")

        self.board_label = tk.Label(self, text="Борд: ")
        self.board_label.pack()

        self.player_frames = []
        for player in simulator.players:
            frame = tk.Frame(self)
            frame.pack()
            label = tk.Label(frame, text=f"{player.name}: стек {player.stack}")
            label.pack()
            self.player_frames.append((frame, label))

        self.log = tk.Text(self, height=10, width=50)
        self.log.pack()

        # Кнопки для управления
        self.start_button = tk.Button(self, text="Начать раздачу", command=self.start_hand)
        self.start_button.pack()

        self.next_button = tk.Button(self, text="Следующая стадия", command=self.next_stage)
        self.next_button.pack()
        self.next_button.config(state=tk.DISABLED)  # Пока не начали

    def start_hand(self):
        self.log.delete(1.0, tk.END)
        self.simulator.start_hand()
        self.update_players()
        self.board_label.config(text="Борд: ")
        self.log.insert(tk.END, "Раздача началась!\n")
        self.next_button.config(state=tk.NORMAL)

    def next_stage(self):
        result = self.simulator.next_stage()

        # Обновляем борд
        board_str = " ".join(c.pretty() for c in self.simulator.community_cards)
        self.board_label.config(text=f"Борд: {board_str}")

        # Обновляем стеки
        self.update_players()

        # Логируем результат
        stage = self.simulator.stages[self.simulator.current_stage - 1] if self.simulator.current_stage > 0 else ""
        if result["action"] == "all_folded":
            self.log.insert(tk.END, f"[{stage}] Все сбросили, {result['winner']} забрал {result['pot']}\n")
            self.next_button.config(state=tk.DISABLED)
        elif result["action"] == "showdown":
            self.log.insert(tk.END,
                            f"[{stage}] Победитель(и): {result['winners']} получили {result['pot'] // len(result['winners'])} каждый\n")
            self.next_button.config(state=tk.DISABLED)
        else:
            self.log.insert(tk.END, f"[{stage}] Банк: {result['pot']}\n")

    def update_players(self):
        for (frame, label), player in zip(self.player_frames, self.simulator.players):
            if player.in_game:
                label.config(text=f"{player.name}: стек {player.stack}")
            else:
                label.config(text=f"{player.name}: выбыл")


if __name__ == "__main__":
    players = [
        Player("Bot1", simple_strategy),
        Player("Bot2", simple_strategy),
        Player("Bot3", simple_strategy),
    ]
    sim = PokerSimulator(players)
    app = PokerGUI(sim)
    app.mainloop()
