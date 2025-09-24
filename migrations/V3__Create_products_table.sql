CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_category ON products (category_id);
CREATE INDEX idx_sku ON products (sku);