🧠 Описание проекта
SwarmClan — сайт статистики игроков Tekken 8 (RU-сегмент), построен на Next.js (TypeScript) и использует внешний API для сбора данных о матчах. Сайт показывает таблицу лидеров, профили игроков и данные о любимых персонажах, рангах и активности.

⚙️ Стек и архитектура
Frontend:

Next.js (App Router, TypeScript)

Tailwind CSS (классы в компонентах)

SSR и динамические маршруты

UI страницы: /app/page.tsx, /app/leaderboard/page.tsx, /app/player/[id]/page.tsx

Backend:

API-роуты /api/leaderboard, /api/player/:id

Node.js + MySQL (через mysql2/promise)

Фоновый fetch скрипт: scripts/fetch-replay.ts

Сервер:

VPS Ubuntu + aaPanel

Nginx + MySQL (phpMyAdmin)

Frontend деплоится на Vercel или на свой сервер (/frontend — корневая папка сайта в /www/wwwroot/swarmclan.ru/)

📦 Структура проекта
swift
Копировать
Редактировать
/frontend
├── app
│   ├── page.tsx                   // Главная: Топ-50 игроков
│   ├── leaderboard/page.tsx       // Полный лидерборд с пагинацией и поиском
│   └── player/[id]/page.tsx       // Страница профиля игрока
├── lib/tekken-data.ts             // Словари персонажей, рангов и т.п.
├── scripts/fetch-replay.ts        // Скрипт загрузки реплеев из API
└── api/leaderboard/route.ts       // API для списка игроков
🔌 Внешнее API
Используется API Tekken 8:
https://wank.wavu.wiki/api/replays

Получение реплеев в формате ?before=timestamp

Скрипт парсит игроков и сохраняет в MySQL (swarmclan_fresh.replays)

Используются поля: p1_*, p2_*, battle_at, battle_type, lang, power, rank, chara_id

🧩 Особенности
Ранговая сортировка: сначала по rank, потом по power

rank_id и chara_id отображаются читаемо через маппинг (tekken-data.ts)

Пагинация на /leaderboard — по 200 игроков с отображением позиции (#)

Поиск по нику, результат показывается отдельно с позицией

✅ Что должен знать ChatGPT
Проект использует Next.js App Router и TypeScript

MySQL и API хостятся на сервере с aaPanel (через Nginx)

Фронт и бэкенд находятся в /frontend

Роуты типа /api/leaderboard, /player/:id уже настроены

Данные собираются с wank.wavu.wiki/api/replays фоновым скриптом

Цель сайта — отображать статистику RU-игроков по Tekken 8