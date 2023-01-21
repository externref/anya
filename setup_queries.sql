CREATE TABLE IF NOT EXISTS greetings (
    guild_id BIGINT PRIMARY KEY NOT NULL,
    accent_color INT DEFAULT 0,
    ignore_bots BOOLEAN DEFAULT false,

    welcome_channel_id BIGINT,
    goodbye_channel_id BIGINT,

    welcome_message VARCHAR(2000) DEFAULT 'Hello {member}, welcome to {#server_name}',
    goodbye_message VARCHAR(2000) DEFAULT '{member} left.' 
);


CREATE TABLE IF NOT EXISTS confession_configs (
    guild_id BIGINT PRIMARY KEY NOT NULL,
    channel_id BIGINT  
);


CREATE TABLE IF NOT EXISTS confession_logs (
    guild_id BIGINT NOT NULL,
    confession_id INT NOT NULL, 
    author_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL
);


CREATE TABLE IF NOT EXISTS confession_bans (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reason VARCHAR(1000) DEFAULT 'No reason provided' 
);