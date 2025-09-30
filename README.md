# POKER
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  
</head>
<body>

<div class="container">

  <h1>🃏 Poker Simulator with AI & GUI</h1>
  <p class="subtitle">Симулятор Texas Hold'em с искусственным интеллектом и графическим интерфейсом</p>



  <h2>🎯 Возможности</h2>
  <ul>
    <li><strong>Полная симуляция раздачи</strong>: Preflop → Flop → Turn → River → Showdown</li>
    <li><strong>Поддержка нескольких игроков</strong> с разными стратегиями</li>
    <li><strong>Графический интерфейс на Tkinter</strong> с изображениями карт и борда</li>
    <li><strong>Цветной лог действий</strong> с эмодзи, этапами и результатами</li>
    <li><strong>Простая система стратегий</strong>: колл, фолд, рейз, блеф</li>
    <li><strong>Логирование всех действий</strong> (включая блефы и вскрытия)</li>
    <li><strong>Расширяемая архитектура</strong> — легко добавить новых ботов</li>
  </ul>

  <h2>🧰 Технологии</h2>
  <ul>
    <li>Python 3.8+</li>
    <li>Tkinter — графический интерфейс</li>
    <li>OOP — объектно-ориентированная структура</li>
    <li>AI/Strategy System — функции-стратегии для ботов</li>
  </ul>

  <h2>🚀 Как запустить</h2>
  <ol>
    <li>Убедитесь, что установлен Python 3.8+</li>
    <li>Запустите GUI командой:</li>
  </ol>
  <pre>python -m gui.poker_gui</pre>
  <p>💡 Все 52 карты находятся в <code>templates/cards/</code> (формат: <code>As.png</code>, <code>Td.png</code>, <code>2c.png</code> и т.д.)</p>

  <h2>🧠 Поддерживаемые стратегии</h2>
  <table border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse: collapse; margin: 15px 0;">
    <tr style="background:#f1f3f5;">
      <th style="text-align:left;">Имя</th>
      <th style="text-align:left;">Описание</th>
    </tr>
    <tr>
      <td><code>simple_strategy</code></td>
      <td>Простой бот: колл/фолд на основе силы руки</td>
    </tr>
    <tr>
      <td><code>monte_carlo_strategy</code></td>
      <td>MC-оценка шансов выигрыша перед действием</td>
    </tr>
    <tr>
      <td><code>bluff_raise</code></td>
      <td>Поддержка блефа и агрессивных рейзов</td>
    </tr>
  </table>

  <p>Можно добавить свою стратегию:</p>
  <pre>def my_strategy(player, community_cards, pot, stage):
    # Возвращает: "fold", "call", "raise_2x", "raise_pot", "bluff_raise_pot"
    return "call"</pre>

  <h2>📁 Структура проекта</h2>
  <pre>
POKER/
├── poker/
│   ├── cards.py        # Карты, колода, парсинг
│   └── evaluator.py    # Оценка комбинаций (пока заглушка)
├── ai/
│   └── basic_strategy.py  # Стратегии ботов
├── templates/
│   └── cards/          # 52 PNG-карты (As.png, Td.png и т.д.)
├── gui/
│   └── poker_gui.py    # Графический интерфейс
├── utils/
│   └── detailed_log.py # Логирование действий
└── main.py             # Пример запуска (опционально)</pre>

  <h2>📈 Планы на будущее</h2>
  <h3>🔮 Расширение функционала</h3>
  <ul>
    <li>[ ] Реализация полной системы оценки рук (<code>evaluator.py</code>)</li>
    <li>[ ] Поддержка side-pot'ов и split банка</li>
    <li>[ ] Множественные раунды ставок с позициями (UTG, BTN, SB, BB)</li>
    <li>[ ] История раздач и экспорт в JSON</li>
  </ul>

  <h3>🤖 Улучшение AI</h3>
  <ul>
    <li>[ ] Обучение бота через reinforcement learning (QLearning, DQN)</li>
    <li>[ ] Поддержка GTO-стратегий</li>
    <li>[ ] Анализ диапазонов оппонентов</li>
  </ul>

  <h3>🎨 Улучшение GUI</h3>
  <ul>
    <li>[ ] Анимация появления карт</li>
    <li>[ ] Подсветка победителя</li>
    <li>[ ] Темы оформления (темная, светлая, покерный стол)</li>
    <li>[ ] Звуки действий (опционально)</li>
  </ul>

  <h3>📊 Визуализация</h3>
  <ul>
    <li>[ ] График изменения стеков по раздачам</li>
    <li>[ ] Heatmap частоты действий</li>
    <li>[ ] Экспорт лога в HTML/PDF</li>
  </ul>

  <h2>🤝 Как внести вклад</h2>
  <p>Проект открыт для улучшений! Вы можете:</p>
  <ul>
    <li>Добавить новую стратегию</li>
    <li>Улучшить оценку рук</li>
    <li>Создать более красивые PNG-карты</li>
    <li>Добавить unit-тесты</li>
    <li>Перевести README на другие языки</li>
  </ul>
  <p>Создавайте <strong>Issues</strong> и <strong>Pull Requests</strong> — любые идеи приветствуются!</p>

  <h2>📄 Лицензия</h2>
  <p>MIT License — свободное использование и модификация.</p>

  <footer>
    🃏 <em>Да побеждает сильнейший (или самый хитрый)!</em>
  </footer>

</div>

</body>
</html>
