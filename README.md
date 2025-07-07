# SwarmClan Tekken 8 Stats Website

Это сайт статистики игроков Tekken 8 для клана SWARM — https://swarmclan.ru  
Проект собирает данные из публичного API и отображает их в виде таблиц, профилей игроков и графиков.

## 🛠️ Технологии

- **Next.js (App Router)** — фронтенд
- **TypeScript** — весь код
- **MySQL** — база данных
- **aaPanel** — управление сервером
- **pm2** — запуск скриптов в фоне
- **Vercel / VPS** — хостинг
- **Tailwind CSS** — стили

## 📦 Структура проекта

/app
/page.tsx ← Главная страница
/leaderboard ← Таблица лидеров (вся Россия)
/player/[id] ← Профиль игрока
/characters ← Топ игроки по персонажам
/api
/leaderboard ← API для получения списка игроков из кеша
/add-player ← API для добавления себя по Polaris ID

/components
RankDistribution.tsx ← График распределения по рангам
AddPlayerModal.tsx ← Модальное окно "Добавить игрока"

/scripts
update-leaderboard-cache.ts ← Скрипт обновления кеша раз в 5 минут

markdown
Копировать
Редактировать

## 📊 База данных (MySQL)

Таблицы:

- `replays` — все загруженные бои из `https://wank.wavu.wiki/api/replays`
- `added_players` — пользователи, добавившие себя (по polaris_id)
- `leaderboard_cache` — готовый список игроков, который обновляется раз в 5 минут

## 🔁 Сбор данных

Бесконечный скрипт в Node.js (`fetch-replay.ts`) каждые 700 секунд делает запрос к API и загружает реплеи в таблицу `replays`.  
Кеш обновляется скриптом `update-leaderboard-cache.ts` и запускается через `pm2` по CRON раз в 5 минут.

## 🧠 Логика API

### /api/leaderboard

Возвращает список топ-игроков:

- фильтрует только тех, у кого язык `ru` **или** кто добавлен вручную через `/api/add-player`
- объединяет p1 и p2 игроков
- группирует по polaris_id
- выбирает лучший ранг и любимого персонажа

### /api/add-player

Добавляет `polaris_id` в таблицу `added_players`, если он найден в реплеях (либо как p1, либо как p2).  
Если уже есть — возвращает `status: "exists"`.  
Если не найден — `status: "not_found"`.

## 💡 Особенности

- 🔍 Автоподсказка по нику на главной
- 📈 График по рангам
- 🕹️ Страница `/characters` с топ-3 игроками по каждому персонажу
- ⏱️ Все запросы идут к кешу, а не к реплеям — это ускоряет сайт

## 🚀 Развертывание

```bash
npm install
npm run build
pm2 start "npx tsx scripts/update-leaderboard-cache.ts" --name update-leaderboard-cache --cron "*/5 * * * *"
pm2 save