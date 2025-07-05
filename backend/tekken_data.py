import requests
import mysql.connector
from datetime import datetime, timedelta
import time
from config import DB_CONFIG  # Вынеси настройки БД в отдельный файл!

# Подключение к БД
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к БД: {err}")
        return None

# Запрос к API и сохранение данных
def fetch_and_save_replays(before_time=None):
    if before_time is None:
        before_time = int(time.time())  # Текущее время в UNIX

    url = "https://wank.wavu.wiki/api/replays?_format=json"
    params = {"before": before_time}
    
    try:
        response = requests.get(url, params=params, headers={"Accept-Encoding": "gzip"})
        response.raise_for_status()
        replays = response.json()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        for replay in replays:
            # Фильтр: только ранговые бои и русскоязычные игроки
            if replay["battle_type"] == 2 and (replay["p1_lang"] == "ru" or replay["p2_lang"] == "ru"):
                # Сохраняем игрока 1 (если русский)
                if replay["p1_lang"] == "ru":
                    save_player(cursor, replay, "p1")
                
                # Сохраняем игрока 2 (если русский)
                if replay["p2_lang"] == "ru":
                    save_player(cursor, replay, "p2")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Успешно сохранено. Следующий before_time: {before_time - 700}")
        return before_time - 700  # Для следующего запроса
    
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")

# Сохранение игрока в БД
def save_player(cursor, replay, player_prefix):
    player_data = {
        "name": replay[f"{player_prefix}_name"],
        "polaris_id": replay[f"{player_prefix}_polaris_id"],
        "power": replay[f"{player_prefix}_power"],
        "lang": replay[f"{player_prefix}_lang"],
        "chara_id": replay[f"{player_prefix}_chara_id"],
        "rank": replay[f"{player_prefix}_rank"],
        "battle_at": datetime.fromtimestamp(replay["battle_at"]).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Проверяем, есть ли игрок уже в БД, и обновляем/добавляем
    cursor.execute("""
        INSERT INTO players (name, polaris_id, power, lang, chara_id, rank, last_battle_time)
        VALUES (%(name)s, %(polaris_id)s, %(power)s, %(lang)s, %(chara_id)s, %(rank)s, %(battle_at)s)
        ON DUPLICATE KEY UPDATE
            power = VALUES(power),
            rank = VALUES(rank),
            last_battle_time = VALUES(last_battle_time)
    """, player_data)

# Пример запуска
if __name__ == "__main__":
    before_time = int(time.time())  # Начать с текущего времени
    for _ in range(10):  # 10 запросов (можно заменить на while True для бесконечного цикла)
        before_time = fetch_and_save_replays(before_time)
        time.sleep(1)  # Задержка, чтобы не превысить лимиты API