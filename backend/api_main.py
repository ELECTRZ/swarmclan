from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Настройки БД
DB_CONFIG = {
    "dbname": "tekkenmatches",
    "user": "tekkenadmin",
    "password": "SD4Mb7Jnc5X5",
    "host": "localhost"
}

# === Твои данные по персонажам и рангам ===
from tekken_data import CHARACTER_MAP, RANK_MAP  # <-- Сюда вставляешь

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.get("/player/{name}")
def get_player(name: str):
    conn = get_db()
    cur = conn.cursor()

    # Попробуем найти игрока как p1
    cur.execute("""
        SELECT 
            p1_name, p1_rank, p1_chara_id, MAX(p1_power), COUNT(*),
            SUM(CASE WHEN winner = 1 THEN 1 ELSE 0 END)
        FROM replays
        WHERE p1_name = %s AND p1_lang = 'ru'
        GROUP BY p1_name, p1_rank, p1_chara_id
        ORDER BY p1_power DESC LIMIT 1
    """, (name,))
    
    data = cur.fetchone()
    if not data:
        cur.execute("""
            SELECT 
                p2_name, p2_rank, p2_chara_id, MAX(p2_power), COUNT(*),
                SUM(CASE WHEN winner = 2 THEN 1 ELSE 0 END)
            FROM replays
            WHERE p2_name = %s AND p2_lang = 'ru'
            GROUP BY p2_name, p2_rank, p2_chara_id
            ORDER BY p2_power DESC LIMIT 1
        """, (name,))
        data = cur.fetchone()

    if not data:
        raise HTTPException(status_code=404, detail="Игрок не найден")

    player_name, rank_num, chara_id, power, total_matches, wins = data
    losses = total_matches - wins

    return {
        "name": player_name,
        "rank": RANK_MAP.get(str(rank_num), "Неизвестный ранг"),
        "character": CHARACTER_MAP.get(str(chara_id), "Неизвестный персонаж"),
        "power": power,
        "total_matches": total_matches,
        "wins": wins,
        "losses": losses
    }

@app.get("/matches")
def get_matches(name: str = None, polaris_id: str = None):
    if not name and not polaris_id:
        return {"error": "Укажите имя или Tekken ID для поиска"}
    
    conn = get_db()
    cur = conn.cursor()
    
    if name:
        cur.execute("""
            SELECT * FROM replays WHERE p1_name = %s OR p2_name = %s
            ORDER BY battle_at DESC LIMIT 20
        """, (name, name))
    elif polaris_id:
        cur.execute("""
            SELECT * FROM replays WHERE p1_polaris_id = %s OR p2_polaris_id = %s
            ORDER BY battle_at DESC LIMIT 20
        """, (polaris_id, polaris_id))

    matches = cur.fetchall()
    return {"matches": matches}

@app.get("/leaderboard")
def get_leaderboard(page: int = 1):
    limit = 50
    offset = (page - 1) * limit

    conn = get_db()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT name, MAX(power), SUM(wins), SUM(losses)
        FROM (
            SELECT 
                p1_name as name, p1_power as power,
                SUM(CASE WHEN winner = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner = 2 THEN 1 ELSE 0 END) as losses
            FROM replays WHERE p1_lang = 'ru' GROUP BY p1_name, p1_power

            UNION ALL

            SELECT 
                p2_name as name, p2_power as power,
                SUM(CASE WHEN winner = 2 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner = 1 THEN 1 ELSE 0 END) as losses
            FROM replays WHERE p2_lang = 'ru' GROUP BY p2_name, p2_power
        ) AS combined
        GROUP BY name
        ORDER BY max_power DESC
        LIMIT {limit} OFFSET {offset};
    """)

    rows = cur.fetchall()
    result = []
    for row in rows:
        name, power, wins, losses = row
        result.append({
            "name": name,
            "max_power": power,
            "wins": wins,
            "losses": losses
        })

    return {"page": page, "leaderboard": result}