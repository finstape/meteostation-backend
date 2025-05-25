DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'admin_telegram_id') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('admin_telegram_id', '12345678', 'int');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'latitude') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('latitude', '59.881234', 'float');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'longitude') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('longitude', '29.906774', 'float');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'sensor_poll_interval_ms') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('sensor_poll_interval_ms', '5000', 'int');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'co2_alert_threshold') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('co2_alert_threshold', '800', 'int');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'tvoc_alert_threshold') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('tvoc_alert_threshold', '150', 'int');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'telegram_bot_token') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('telegram_bot_token', 'token', 'str');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM settings WHERE key = 'telegram_webhook_url') THEN
        INSERT INTO settings (key, value, type)
        VALUES ('telegram_webhook_url', 'https://your.domain.com/api/v1/webhook', 'str');
    END IF;
END
$$;
