import os
import tkinter as tk
from tkinter import ttk
from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import simple_strategy, monte_carlo_strategy


class PokerGUI(tk.Tk):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.title("🃏 Poker Simulator")
        self.geometry("1200x800")
        self.configure(bg="#0d3b2a")  # Тёмно-зелёный фон (покерный стол)

        # Путь к папке с картами
        self.cards_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "cards")
        if not os.path.exists(self.cards_dir):
            print(f"⚠️ Папка с картами не найдена: {self.cards_dir}")
            self.cards_dir = None

        # Заголовок
        title = tk.Label(self, text="🃏 Poker Simulator", font=("Arial Black", 24), bg="#0d3b2a", fg="white")
        title.pack(pady=10)

        # Фрейм для борда
        board_frame = tk.Frame(self, bg="#0d3b2a")
        board_frame.pack(pady=10)

        # Метка для текста борда
        self.board_label = tk.Label(board_frame, text="Борд: ", font=("Arial", 16, "bold"), bg="#0d3b2a", fg="white")
        self.board_label.pack(side=tk.LEFT, padx=5)

        # Фрейм для изображений борда
        self.board_images_frame = tk.Frame(board_frame, bg="#0d3b2a")
        self.board_images_frame.pack(side=tk.LEFT, padx=5)

        # Фрейм для игроков
        players_frame = tk.Frame(self, bg="#0d3b2a")
        players_frame.pack(pady=20, fill=tk.X, padx=20)

        self.player_frames = []
        for i, player in enumerate(self.simulator.players):
            frame = tk.Frame(players_frame, bg="#1a523f", relief=tk.RAISED, bd=2)
            frame.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

            # Имя и стек
            name_label = tk.Label(frame, text=f"{player.name}", font=("Arial", 14, "bold"), bg="#1a523f", fg="white")
            name_label.pack(pady=5)

            stack_label = tk.Label(frame, text=f"стек: {player.stack}", font=("Arial", 12), bg="#1a523f", fg="#ffd700")
            stack_label.pack(pady=2)

            # Фрейм для карт
            card_frame = tk.Frame(frame, bg="#1a523f")
            card_frame.pack(pady=5)

            # Сохраняем ссылки
            player.card_images = []

            self.player_frames.append((frame, name_label, stack_label, card_frame))

        # Лог
        log_frame = tk.Frame(self, bg="#0d3b2a")
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.log = tk.Text(log_frame, height=8, width=100, font=("Courier", 11), bg="#000", fg="#fff", wrap=tk.WORD,
                           relief=tk.SUNKEN, bd=2)
        self.log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log.insert(tk.END, "🎮 Добро пожаловать в Poker Simulator!\n")

        # Кнопки
        btn_frame = tk.Frame(self, bg="#0d3b2a")
        btn_frame.pack(pady=10)

        self.start_button = tk.Button(btn_frame, text="▶️ Начать раздачу", command=self.start_hand, bg="#2ecc71",
                                      fg="white", font=("Arial", 12, "bold"), relief=tk.RAISED, bd=3)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(btn_frame, text="⏩ Следующая стадия", command=self.next_stage, state=tk.DISABLED,
                                     bg="#3498db", fg="white", font=("Arial", 12, "bold"), relief=tk.RAISED, bd=3)
        self.next_button.pack(side=tk.LEFT, padx=10)

    def update_board(self):
        """Обновляет изображения борда."""
        # Очищаем старые карты
        for widget in self.board_images_frame.winfo_children():
            widget.destroy()

        # Если нет карт — показываем текст
        if not self.simulator.community_cards:
            label = tk.Label(self.board_images_frame, text="Борд пуст", font=("Arial", 12), bg="#0d3b2a", fg="white")
            label.pack()
            return

        # Отображаем каждую карту
        for i, card in enumerate(self.simulator.community_cards):
            filename = f"{card.rank_str()}{card.suit}.png"
            path = os.path.join(self.cards_dir, filename) if self.cards_dir else None

            try:
                if not self.cards_dir or not os.path.exists(path):
                    raise FileNotFoundError(f"Файл не найден: {path}")

                img = tk.PhotoImage(file=path)
                img = img.subsample(3)  # уменьшаем

                # Создаём рамку с тенью
                card_container = tk.Frame(self.board_images_frame, bg="#0d3b2a", highlightbackground="#333",
                                          highlightthickness=2)
                card_container.pack(side=tk.LEFT, padx=5)

                label = tk.Label(card_container, image=img, bg="#0d3b2a")
                label.image = img
                label.pack()

            except Exception as e:
                print(f"❌ Не удалось загрузить карту борда: {path} — {e}")
                label = tk.Label(self.board_images_frame, text=card.pretty(), font=("Arial", 14), bg="#0d3b2a",
                                 fg="white")
                label.pack(side=tk.LEFT, padx=5)

    def start_hand(self):
        """Начинаем новую раздачу."""
        self.log.delete(1.0, tk.END)
        self.simulator.start_hand()
        self.update_players()
        self.board_label.config(text="Борд: ")
        self.update_board()
        self.log.insert(tk.END, "🎮 Добро пожаловать в Poker Simulator!\n", ("stage",))
        self.log.insert(tk.END, "🃏 Раздача началась! Стартовый банк: 0\n", ("stage",))
        self.start_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)

    def next_stage(self):
        result = self.simulator.next_stage()
        if not result:
            return

        # Обновляем текст борда
        board_str = " ".join(c.pretty() for c in self.simulator.community_cards)
        self.board_label.config(text=f"Борд: {board_str}")

        # Обновляем GUI игроков и борд
        self.update_players()
        self.update_board()

        # 🔥 Красивый лог — только один раз!
        self.pretty_log(result)

        # Подсветка блефа (если был)
        stage = self.simulator.stages[self.simulator.current_stage - 1] if self.simulator.current_stage > 0 else ""

        if hasattr(self.simulator.logger, 'last_action') and self.simulator.logger.last_action == 'bluff_raise':
            player = self.simulator.logger.last_player
            log_line = f"[{stage}] 🎭 {player} сделал БЛЕФ-РЕЙЗ!\n"
            self.log.insert(tk.END, log_line, ("action",))
            self.log.see(tk.END)

        # Деактивация кнопок при завершении
        if result.get("action") == "all_folded" or result.get("action") == "showdown":
            self.next_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)

    def update_players(self):
        """Обновляет стеки и карты игроков."""
        for (frame, name_label, stack_label, card_frame), player in zip(self.player_frames, self.simulator.players):
            if not player.in_game:
                name_label.config(text=f"{player.name} ❌", fg="red")
                stack_label.config(text="выбыл", fg="red")
                # Очищаем карты
                for widget in card_frame.winfo_children():
                    widget.destroy()
                player.card_images = []
            else:
                # Обновляем стек
                name_label.config(text=player.name, fg="white")
                stack_label.config(text=f"стек: {player.stack}", fg="#ffd700")

                # Очищаем старые карты
                for widget in card_frame.winfo_children():
                    widget.destroy()

                # Показываем новые карты
                player.card_images = []
                for card in player.hand:
                    filename = f"{card.rank_str()}{card.suit}.png"
                    path = os.path.join(self.cards_dir, filename) if self.cards_dir else None

                    try:
                        if not self.cards_dir or not os.path.exists(path):
                            raise FileNotFoundError(f"Файл не найден: {path}")

                        img = tk.PhotoImage(file=path)
                        img = img.subsample(3)  # уменьшаем

                        # Рамка с тенью
                        card_container = tk.Frame(card_frame, bg="#1a523f", highlightbackground="#333",
                                                  highlightthickness=2)
                        card_container.pack(side=tk.LEFT, padx=3)

                        label_card = tk.Label(card_container, image=img, bg="#1a523f")
                        label_card.image = img
                        label_card.pack()

                        player.card_images.append(img)

                    except Exception as e:
                        print(f"❌ Не удалось загрузить карту игрока: {path} — {e}")
                        label_card = tk.Label(card_frame, text=card.pretty(), font=("Arial", 12), bg="#1a523f",
                                              fg="white")
                        label_card.pack(side=tk.LEFT, padx=3)

    def pretty_log(self, result):
        """Красиво выводит результат в лог."""
        stage = self.simulator.stages[
            self.simulator.current_stage - 1] if self.simulator.current_stage > 0 else "Unknown"
        pot = result.get('pot', 0)
        action = result.get('action', 'continue')

        # Эмодзи для этапов
        stage_emoji = {
            'Preflop': '🃏',
            'Flop': '💥',
            'Turn': '🌀',
            'River': '🌊',
            'Showdown': '🏆',
            'AllFolded': '🎉'
        }.get(stage, '🎲')

        # Теги цветов
        self.log.tag_configure("stage", foreground="#ffd700", font=("Courier", 11, "bold"))
        self.log.tag_configure("bank", foreground="#00ff00", font=("Courier", 11))
        self.log.tag_configure("winner", foreground="#ffcc00", font=("Courier", 11, "bold"))

        log_line = f"[{stage_emoji} {stage}] "

        if action == "all_folded":
            winner = result.get("winner", "???")
            log_line += f"🎉 Все сбросили! {winner} забирает {pot}\n"
            self.log.insert(tk.END, log_line, ("winner",))

        elif action == "showdown":
            winners = result.get("winners", [])
            if not winners:
                log_line += f"🏆 Никто не победил (банк: {pot})\n"
                self.log.insert(tk.END, log_line, ("bank",))
            else:
                split_pot = pot // len(winners)
                winners_str = ", ".join(winners)
                log_line += f"🏆 Победитель(и): {winners_str} → +{split_pot} каждый\n"
                self.log.insert(tk.END, log_line, ("winner",))
        else:
            # Обычный ход: Preflop, Flop, Turn, River
            community_cards = result.get('community_cards', [])
            cards_str = " ".join(c.pretty() for c in community_cards) if community_cards else "—"
            log_line += f"💰 Банк: {pot} | Борд: {cards_str}\n"
            self.log.insert(tk.END, log_line, ("bank",))

        self.log.see(tk.END)

if __name__ == "__main__":
    players = [
        Player("SimpleBot", simple_strategy),
        Player("MCCBot", monte_carlo_strategy),
        Player("PassiveBot", simple_strategy),
    ]
    sim = PokerSimulator(players, big_blind=20)
    app = PokerGUI(sim)
    app.mainloop()
