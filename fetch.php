<?php
date_default_timezone_set('Europe/Moscow');

// Подключение к MySQL
$host = 'localhost';
$dbname = 'swarmclan_db';
$username = 'swarmclan_user';
$password = 'c467yz';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die('❌ Ошибка подключения к базе данных: ' . $e->getMessage());
}

// Проверяем, установлен ли curl
if (!function_exists('curl_init')) {
    die('❌ Ошибка: модуль curl не установлен!');
}

// Получаем сырые матчи из API
function fetchReplays($before, $pdo) {
    $url = "https://wank.wavu.wiki/api/replays?before=" . $before;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_ENCODING, ''); // важно для сжатия
    curl_setopt($ch, CURLOPT_USERAGENT, 'MyTekkenApp/1.0'); // важно для API
    $response = curl_exec($ch);

    if ($response === false) {
        die('❌ Ошибка cURL: ' . curl_error($ch));
    }

    curl_close($ch);

    return json_decode($response, true);
}

// Функция для очистки старых данных
function cleanOldData($pdo) {
    // Удаляем записи старше 30 дней
    $stmt = $pdo->prepare("DELETE FROM replays WHERE created_at < DATE_SUB(CURDATE(), INTERVAL 30 DAY)");
    $stmt->execute();
}

// Функция для сохранения матча в базу
function saveMatchToDB($match, $pdo) {
    $stmt = $pdo->prepare("
        INSERT INTO replays (
            battle_at, battle_id, battle_type, game_version,
            p1_name, p1_lang, p1_power, p1_rank, p1_rating_before, p1_rating_change,
            p2_name, p2_lang, p2_power, p2_rank, p2_rating_before, p2_rating_change,
            stage_id, winner
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");
    $stmt->execute([
        $match['battle_at'],
        $match['battle_id'],
        $match['battle_type'],
        $match['game_version'],
        $match['p1_name'] ?? null,
        $match['p1_lang'] ?? null,
        $match['p1_power'] ?? null,
        $match['p1_rank'] ?? null,
        $match['p1_rating_before'] ?? null,
        $match['p1_rating_change'] ?? null,
        $match['p2_name'] ?? null,
        $match['p2_lang'] ?? null,
        $match['p2_power'] ?? null,
        $match['p2_rank'] ?? null,
        $match['p2_rating_before'] ?? null,
        $match['p2_rating_change'] ?? null,
        $match['stage_id'] ?? null,
        $match['winner'] ?? null
    ]);
}

// Очистка старых данных
cleanOldData($pdo);

// Сбор данных
$allMatches = [];
$before = time(); // начальное значение времени

for ($i = 0; $i < 3; $i++) {
    $matches = fetchReplays($before, $pdo);
    if (empty($matches)) break;

    foreach ($matches as $match) {
        // Фильтруем только ранговые бои
        if ($match['battle_type'] == 2) {
            saveMatchToDB($match, $pdo);
        }
    }

    // Обновляем before для следующего запроса
    $before = end($matches)['battle_at'] - 1;
    sleep(1); // пауза между запросами
}

echo "✅ Данные успешно загружены и сохранены в базу данных";