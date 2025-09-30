import os
import tkinter as tk
from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import simple_strategy, monte_carlo_strategy


class PokerGUI(tk.Tk):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.title("Poker Simulator")

        # Путь к папке с картами
        self.cards_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "cards")
        if not os.path.exists(self.cards_dir):
            print(f"⚠ Папка с картами не найдена: {self.cards_dir}")

        # Метка для борда
        self.board_label = tk.Label(self, text="Борд: ", font=("Courier", 14))
        self.board_label.pack(pady=5)

        # Отображение игроков
        self.player_frames = []
        for player in simulator.players:
            frame = tk.Frame(self)
            frame.pack(pady=2)
            label = tk.Label(frame, text=f"{player.name}: стек {player.stack}", font=("Arial", 12))
            label.pack()
            self.player_frames.append((frame, label))

        # Лог действий
        self.log = tk.Text(self, height=12, width=60, font=("Courier", 10), bg="black", fg="white")
        self.log.pack(pady=10)
        self.log.insert(tk.END, "Добро пожаловать в Poker Simulator!\n")

        # Кнопки
        self.start_button = tk.Button(self, text="Начать раздачу", command=self.start_hand, bg="green", fg="white")
        self.start_button.pack(pady=2)

        self.next_button = tk.Button(self, text="Следующая стадия", command=self.next_stage, state=tk.DISABLED)
        self.next_button.pack(pady=2)

    def update_board(self):
        """Отображает борд как изображения карт."""
        board_frame = tk.Frame(self)
        board_frame.place(x=100, y=100)

        for i, card in enumerate(self.simulator.community_cards):
            filename = f"{card.rank_str()}{card.suit}.png"
            path = os.path.join(self.cards_dir, filename)
            try:
                img = tk.PhotoImage(file=path)
                img = img.subsample(2)  # уменьшаем в 2 раза
                label = tk.Label(board_frame, image=img)
                label.image = img  # сохраняем ссылку
                label.grid(row=0, column=i, padx=5, pady=5)
            except Exception as e:
                print(f"Не найдена карта: {path} — {e}")

    def start_hand(self):
        """Начинаем новую раздачу."""
        self.log.delete(1.0, tk.END)
        self.simulator.start_hand()
        self.update_players()
        self.board_label.config(text="Борд: ")
        self.log.insert(tk.END, "🃏 Раздача началась!\n")
        self.start_button.config(state=tk.DISABLED)
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

        if hasattr(self.simulator.logger, 'last_action') and self.simulator.logger.last_action == 'bluff_raise':
            self.log.insert(tk.END, f"[{stage}] 🎭 {self.simulator.logger.last_player} сделал БЛЕФ-РЕЙЗ!\n")

        if result.get("action") == "all_folded":
            self.log.insert(tk.END, f"[{stage}] 🎉 Все сбросили! {result['winner']} забирает {result['pot']}\n")
            self.next_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
        elif result.get("action") == "showdown":
            winners = result["winners"]
            if winners:
                split_pot = result["pot"] // len(winners)
                self.log.insert(tk.END,
                                f"[{stage}] 🏆 Победитель(и): {winners} → +{split_pot} каждый\n")
            else:
                self.log.insert(tk.END, f"[{stage}] 🏆 Никто не победил (банк: {result['pot']})\n")
            self.next_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
        else:
            self.log.insert(tk.END, f"[{stage}] 💰 Банк: {self.simulator.pot}\n")

        self.log.see(tk.END)

    def update_players(self):
        """Обновляем отображение стеков игроков, включая подсветку блефа и карты."""
        for (frame, label), player in zip(self.player_frames, self.simulator.players):
            if not player.in_game:
                label.config(text=f"{player.name}: выбыл", fg="red", image=None, compound=tk.LEFT)
            else:
                hand_cards = player.hand
                card_images = []
                for card in hand_cards:
                    filename = f"{card.rank_str()}{card.suit}.png"
                    path = os.path.join(self.cards_dir, filename)
                    try:
                        img = tk.PhotoImage(file=path)
                        img = img.subsample(2)  # уменьшаем в 2 раза
                        card_images.append(img)
                    except Exception as e:
                        print(f"Не найдена карта: {path} — {e}")
                        continue

                # Сохраняем изображения, чтобы они не удалились
                player.card_images = card_images

                text = f"{player.name}: стек {player.stack}"
                if card_images:
                    label.config(image=card_images[0], compound=tk.LEFT, text=text)
                else:
                    label.config(text=text, image=None, compound=tk.LEFT)


if __name__ == "__main__":
    players = [
        Player("SimpleBot", simple_strategy),
        Player("MCCBot", monte_carlo_strategy),
        Player("PassiveBot", simple_strategy),
    ]
    sim = PokerSimulator(players, big_blind=20)
    app = PokerGUI(sim)
    app.mainloop()
