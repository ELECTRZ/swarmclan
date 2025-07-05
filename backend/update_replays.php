#!/www/server/php/84/bin/php
<?php
// Настройка логов
$logFile = __DIR__.'/../logs/api_update.log';
file_put_contents($logFile, "\n[".date('Y-m-d H:i:s')."] START =====\n", FILE_APPEND);

// 1. Подключение к БД
$host = 'localhost';
$dbname = 'swarmclan_db';
$username = 'swarmclan_user';
$password = 'c467yz';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    file_put_contents($logFile, "[".date('H:i:s')."] DB: Connected\n", FILE_APPEND);
} catch (PDOException $e) {
    file_put_contents($logFile, "[".date('H:i:s')."] DB ERROR: ".$e->getMessage()."\n", FILE_APPEND);
    die();
}

// 2. Определяем временной диапазон (текущее время минус 700 сек)
$before = time();
$after = $before - 700;

// 3. Запрос к API
$apiUrl = "https://wank.wavu.wiki/api/replays?_format=json&before=$before";
file_put_contents($logFile, "[".date('H:i:s')."] API: Requesting $apiUrl (Range: ".date('H:i:s', $after)." - ".date('H:i:s', $before).")\n", FILE_APPEND);

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => $apiUrl,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => 'gzip',
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => ['Accept: application/json']
]);
$response = curl_exec($ch);
curl_close($ch);

// 4. Обработка данных
$data = json_decode($response, true);
$newRecords = 0;
$updatedRecords = 0;

foreach ($data as $replay) {
    // Фильтр: только ранговые бои и русскоязычные игроки
    if (($replay['battle_type'] ?? 0) == 2 && 
        (($replay['p1_lang'] ?? '') == 'ru' || ($replay['p2_lang'] ?? '') == 'ru')) {
        
        try {
            $stmt = $pdo->prepare("
                INSERT INTO replays (...) VALUES (...)
                ON DUPLICATE KEY UPDATE
                    p1_power = VALUES(p1_power),
                    p1_rank = VALUES(p1_rank),
                    p2_power = VALUES(p2_power),
                    p2_rank = VALUES(p2_rank)
            ");
            
            // ... (полный код вставки из предыдущих примеров)
            
            if ($stmt->rowCount() > 0) {
                $stmt->rowCount() == 1 ? $newRecords++ : $updatedRecords++;
            }
        } catch (PDOException $e) {
            file_put_contents($logFile, "[".date('H:i:s')."] DB ERROR: ".$e->getMessage()."\n", FILE_APPEND);
        }
    }
}

file_put_contents($logFile, "[".date('H:i:s')."] DONE: Added $newRecords new, updated $updatedRecords records (Time range: ".date('H:i:s', $after)." - ".date('H:i:s', $before).")\n", FILE_APPEND);
?>