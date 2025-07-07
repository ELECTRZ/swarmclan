import requests
import psycopg2
import time

# === Настройки БД ===
DB_CONFIG = {
    "dbname": "tekkenmatches",
    "user": "tekkenadmin",
    "password": "SD4Mb7Jnc5X5",
    "host": "localhost"
}

# === Подключение к PostgreSQL ===
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# === Создание таблицы ===
def init_db(conn):
    print("🔧 [DEBUG] Вызвана функция init_db")
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS replays (
                    battle_id TEXT PRIMARY KEY,
                    battle_at INTEGER,
                    p1_name TEXT,
                    p1_polaris_id TEXT,
                    p1_lang TEXT,
                    p1_power INTEGER,
                    p1_rank INTEGER,
                    p1_chara_id INTEGER,
                    p1_rounds INTEGER,
                    p1_rating_before INTEGER,
                    p1_rating_change INTEGER,
                    p2_name TEXT,
                    p2_polaris_id TEXT,
                    p2_lang TEXT,
                    p2_power INTEGER,
                    p2_rank INTEGER,
                    p2_chara_id INTEGER,
                    p2_rounds INTEGER,
                    p2_rating_before INTEGER,
                    p2_rating_change INTEGER,
                    winner INTEGER,
                    stage_id INTEGER,
                    battle_type INTEGER,
                    game_version TEXT
                )
            ''')
            conn.commit()
            print("✅ Таблица replays успешно создана или уже существует.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
        conn.rollback()

# === Получение актуального before из API ===
def get_latest_before():
    url = "https://wank.wavu.wiki/api/replays?_format=json"
    print("🔄 Получаем актуальный before...")
    try:
        response = requests.get(url, headers={"Accept-Encoding": "gzip, deflate"}, timeout=10)
        if response.status_code != 200:
            print(f"❌ Ошибка при получении before: {response.status_code}")
            return None

        replays = response.json()
        if not replays:
            print("❌ Нет данных в ответе")
            return None

        latest_battle = max(replays, key=lambda b: b["battle_at"])
        before = latest_battle["battle_at"]
        print(f"🕒 Последний battle_at: {before}")
        return before
    except Exception as e:
        print(f"[Ошибка при получении before]: {e}")
        return None

# === Сохранение одного боя ===
def save_battle(conn, battle):
    with conn.cursor() as cur:
        try:
            cur.execute('''
                INSERT INTO replays VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (battle_id) DO NOTHING
            ''', (
                battle["battle_id"],
                battle["battle_at"],
                battle.get("p1_name", ""),
                battle.get("p1_polaris_id", ""),
                battle.get("p1_lang", ""),
                battle.get("p1_power", None),
                battle.get("p1_rank", None),
                battle.get("p1_chara_id", None),
                battle.get("p1_rounds", None),
                battle.get("p1_rating_before", None),
                battle.get("p1_rating_change", None),
                battle.get("p2_name", ""),
                battle.get("p2_polaris_id", ""),
                battle.get("p2_lang", ""),
                battle.get("p2_power", None),
                battle.get("p2_rank", None),
                battle.get("p2_chara_id", None),
                battle.get("p2_rounds", None),
                battle.get("p2_rating_before", None),
                battle.get("p2_rating_change", None),
                battle.get("winner", None),
                battle.get("stage_id", None),
                battle.get("battle_type", None),
                battle.get("game_version", "")
            ))
            print(f"✅ Успешно сохранили бой {battle['battle_id']}")
            conn.commit()
        except Exception as e:
            print(f"[❌ Ошибка при сохранении]: {e}")
            conn.rollback()

# === Основной цикл загрузки ===
def fetch_and_save():
    conn = connect_db()
    init_db(conn)

    # Получаем начальное значение before
    before = get_latest_before() or 1751405520  # дефолтное значение из документации

    while True:
        url = f" https://wank.wavu.wiki/api/replays?before={before}"
        print(f"📡 Запрашиваем данные с {url}...")

        response = requests.get(url, headers={"Accept-Encoding": "gzip, deflate"}, timeout=10)

        if response.status_code != 200:
            print(f"❌ Ошибка: {response.status_code}. Ждём 60 секунд...")
            time.sleep(60)
            continue

        try:
            replays = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            time.sleep(60)
            continue

        count = 0
        for battle in replays:
            if (battle.get("p1_lang") == "ru" or battle.get("p2_lang") == "ru") and battle.get("battle_type") == 2:
                save_battle(conn, battle)
                count += 1

        print(f"📥 Получено {len(replays)} боёв за период.")
        print(f"✅ Сохранено {count} русскоязычных ранговых боёв")

        if replays:
            before = replays[-1]["battle_at"] - 1
            print(f"🕒 Следующий before: {before}")

        time.sleep(600)  # ждём 10 минут перед следующим запросом

# === Точка входа ===
if __name__ == "__main__":
    fetch_and_save()