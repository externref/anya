CREATE TABLE IF NOT EXISTS greetings (
    guild_id BIGINT PRIMARY KEY NOT NULL,
    accent_color INT DEFAULT 0,
    ignore_bots BOOLEAN DEFAULT false,

    welcome_channel_id BIGINT,
    goodbye_channel_id BIGINT,

    welcome_message VARCHAR(2000) DEFAULT 'Hello {member}, welcome to {guild}',
    goodbye_message VARCHAR(2000) DEFAULT '{member} left.' 
);

