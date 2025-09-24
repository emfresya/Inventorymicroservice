CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(client_id) ON DELETE RESTRICT,
    status_id SMALLINT NOT NULL DEFAULT 1 REFERENCES order_statuses(status_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_sum NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    notes TEXT NULL
);

CREATE INDEX idx_client ON orders (client_id);
CREATE INDEX idx_status ON orders (status_id);
CREATE INDEX idx_date ON orders (order_date);