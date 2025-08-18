from poker.simulator import PokerSimulator, Player
from ai.basic_strategy import simple_strategy, monte_carlo_strategy, aggressive_strategy

# Создаём игроков
positions = ["UTG", "CO", "BTN"]

players = [
    Player("UTG_Bot", simple_strategy, position="UTG"),
    Player("CO_Bot", monte_carlo_strategy, position="CO"),
    Player("BTN_Bot", aggressive_strategy, position="BTN"),
]

# Создаём симулятор
sim = PokerSimulator(players, big_blind=20)

print(f"Старт игры: {len(players)} игроков")
print("Стратегии: SimpleBot (простая), MCCBot (Монте-Карло)")

# Сыграем 3 раздачи
for hand_num in range(3):
    print(f"\n--- 🃏 Раздача {hand_num + 1} ---")
    sim.start_hand()

    # Проходим все стадии
    for stage_name in ["Preflop", "Flop", "Turn", "River"]:
        result = sim.next_stage()
        print(f"[{stage_name}] Банк: {sim.pot}")

        if result.get("action") == "all_folded":
            print(f"🎉 {result['winner']} забирает {result['pot']}")
            break
        elif result.get("action") == "showdown":
            winners = result["winners"]
            if winners:
                split_pot = result["pot"] // len(winners)
                print(f"🏆 Победители: {winners} → +{split_pot} каждый")
            else:
                print(f"🏆 Никто не победил (банк: {result['pot']})")
            break

    # Показываем стеки после раздачи
    stacks = " | ".join(f"{p.name}: {p.stack}" for p in players)
    print(f"📊 Стеки: {stacks}")


