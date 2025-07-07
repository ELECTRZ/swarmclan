import psycopg2

# Настройки подключения к БД
DB_CONFIG = {
    "dbname": "tekkenstats",
    "user": "tekkenuser",
    "password": "H3x46PbekDZT",
    "host": "localhost"
}

try:
    # Подключение к базе данных
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Создание тестовой таблицы
    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL
        )
    """)
    
    # Добавление тестовой записи
    cur.execute("""
        INSERT INTO test_table (message) VALUES (%s)
    """, ("Тестовое сообщение от Python!",))
    
    # Сохраняем изменения
    conn.commit()
    
    print("✅ Успешно подключились к БД!")
    print("✅ Таблица test_table создана (или уже существует).")
    print("✅ Запись добавлена в таблицу.")

    # Выводим содержимое таблицы
    cur.execute("SELECT * FROM test_table;")
    rows = cur.fetchall()
    print("\n📋 Содержимое таблицы test_table:")
    for row in rows:
        print(row)

except Exception as e:
    print(f"❌ Ошибка при работе с PostgreSQL: {e}")

finally:
    # Закрываем соединение
    if 'conn' in locals():
        cur.close()
        conn.close()
        print("\n🔌 Соединение с БД закрыто.")
