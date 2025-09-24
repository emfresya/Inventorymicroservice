CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    path VARCHAR(1024) NOT NULL,
    level INT NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX uk_category_path ON categories (path);
CREATE INDEX idx_parent ON categories (parent_id);
CREATE INDEX idx_path ON categories (path);