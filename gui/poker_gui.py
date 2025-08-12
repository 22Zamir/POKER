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

        self.next_button = tk.Button(self, text="Следующая раздача", command=self.play_hand)
        self.next_button.pack()

    def play_hand(self):
        self.log.delete(1.0, tk.END)
        result = self.simulator.play_hand(verbose=False)

        # Обновляем борд
        community_cards = getattr(self.simulator, 'community_cards', [])
        self.board_label.config(text="Борд: " + ' '.join(str(c) for c in community_cards))

        # Обновляем стеки и логи
        for (frame, label), player in zip(self.player_frames, self.simulator.players):
            label.config(text=f"{player.name}: стек {player.stack}")
            self.log.insert(tk.END, f"{player.name}: {player.hand}\n")

        winners = result.get("winners", [])
        self.log.insert(tk.END, f"\nПобедитель(и): {winners}\n")


if __name__ == "__main__":
    players = [
        Player("Bot1", simple_strategy),
        Player("Bot2", simple_strategy),
        Player("Bot3", simple_strategy),
    ]
    sim = PokerSimulator(players)

    app = PokerGUI(sim)
    app.mainloop()