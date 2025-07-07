#!/www/server/php/84/bin/php
<?php
// Настройка логов
$logFile = __DIR__.'/../logs/init_load.log';
file_put_contents($logFile, "=== Начальная загрузка данных ===\n", FILE_APPEND);

// Параметры
$end_time = time();
$start_time = $end_time - (30 * 24 * 3600); // 30 дней назад
$chunk_size = 700;

// Подключение к БД
$host = 'localhost';
$dbname = 'swarmclan_db';
$username = 'swarmclan_user';
$password = 'c467yz';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    file_put_contents($logFile, "DB ERROR: ".$e->getMessage()."\n", FILE_APPEND);
    die();
}

// Основной цикл
for ($before = $end_time; $before > $start_time; $before -= $chunk_size) {
    $after = $before - $chunk_size;
    file_put_contents($logFile, "Processing: ".date('Y-m-d H:i:s', $after)." to ".date('Y-m-d H:i:s', $before)."\n", FILE_APPEND);
    
    $apiUrl = "https://wank.wavu.wiki/api/replays?_format=json&before=$before";
    file_put_contents($logFile, "[".date('H:i:s')."] API: Requesting $apiUrl\n", FILE_APPEND);

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

    // Обработка данных
    $data = json_decode($response, true);
    $totalRecords = 0;
    
    if (is_array($data)) {
        foreach ($data as $replay) {
            if (($replay['battle_type'] ?? 0) == 2 && ($replay['p1_lang'] ?? '') == 'ru') {
                try {
                    $stmt = $pdo->prepare("
                        INSERT INTO replays (
                            battle_at, battle_id, battle_type, game_version,
                            p1_name, p1_polaris_id, p1_lang, p1_power, p1_rank,
                            p1_rating_before, p1_rating_change, p1_chara_id,
                            p2_name, p2_lang, p2_power, p2_rank,
                            p2_rating_before, p2_rating_change,
                            stage_id, winner
                        ) VALUES (
                            :battle_at, :battle_id, :battle_type, :game_version,
                            :p1_name, :p1_polaris_id, :p1_lang, :p1_power, :p1_rank,
                            :p1_rating_before, :p1_rating_change, :p1_chara_id,
                            :p2_name, :p2_lang, :p2_power, :p2_rank,
                            :p2_rating_before, :p2_rating_change,
                            :stage_id, :winner
                        )
                        ON DUPLICATE KEY UPDATE
                            p1_power = VALUES(p1_power),
                            p1_rank = VALUES(p1_rank),
                            p2_power = VALUES(p2_power),
                            p2_rank = VALUES(p2_rank)
                    ");
                    
                    $stmt->execute([
                        ':battle_at' => $replay['battle_at'] ?? time(),
                        ':battle_id' => $replay['battle_id'] ?? '',
                        ':battle_type' => $replay['battle_type'] ?? 0,
                        ':game_version' => $replay['game_version'] ?? 0,
                        ':p1_name' => $replay['p1_name'] ?? 'Unknown',
                        ':p1_polaris_id' => $replay['p1_polaris_id'] ?? '',
                        ':p1_lang' => $replay['p1_lang'] ?? '',
                        ':p1_power' => $replay['p1_power'] ?? 0,
                        ':p1_rank' => $replay['p1_rank'] ?? 0,
                        ':p1_rating_before' => $replay['p1_rating_before'] ?? 0,
                        ':p1_rating_change' => $replay['p1_rating_change'] ?? 0,
                        ':p1_chara_id' => $replay['p1_chara_id'] ?? 0,
                        ':p2_name' => $replay['p2_name'] ?? 'Unknown',
                        ':p2_lang' => $replay['p2_lang'] ?? '',
                        ':p2_power' => $replay['p2_power'] ?? 0,
                        ':p2_rank' => $replay['p2_rank'] ?? 0,
                        ':p2_rating_before' => $replay['p2_rating_before'] ?? 0,
                        ':p2_rating_change' => $replay['p2_rating_change'] ?? 0,
                        ':stage_id' => $replay['stage_id'] ?? 0,
                        ':winner' => $replay['winner'] ?? 0
                    ]);
                    
                    $totalRecords++;
                } catch (PDOException $e) {
                    file_put_contents($logFile, "[".date('H:i:s')."] DB ERROR: ".$e->getMessage()."\n", FILE_APPEND);
                }
            }
        }
    }
    
    file_put_contents($logFile, "[".date('H:i:s')."] Added/updated $totalRecords records\n", FILE_APPEND);
    sleep(1);
}

file_put_contents($logFile, "=== Загрузка завершена ===\n", FILE_APPEND);
?>