CREATE TABLE loyalty_card (
    loyalty_card_id SERIAL PRIMARY KEY,
    num_transactions INTEGER NOT NULL DEFAULT 0,
    num_users INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    loyalty_card_id INTEGER,
    hashed_password VARCHAR(255) NOT NULL,
    FOREIGN KEY (loyalty_card_id) REFERENCES loyalty_card (loyalty_card_id) ON DELETE SET NULL
);


CREATE TABLE coupon (
    coupon_id SERIAL PRIMARY KEY AUTOINCREMENT,
    coupon_value INTEGER NOT NULL,
    loyalty_card_id INTEGER NOT NULL,
    FOREIGN KEY (loyalty_card_id) REFERENCES loyalty_card (loyalty_card_id) ON DELETE SET NULL
);