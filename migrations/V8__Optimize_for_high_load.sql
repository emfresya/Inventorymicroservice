-- 1. Добавляем root_category_id в products
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS root_category_id INT REFERENCES categories(category_id) ON DELETE RESTRICT;

-- Заполняем существующие данные
UPDATE products
SET root_category_id = CAST(
    split_part(trim(leading '/' from trim(trailing '/' from cat.path)), '/', 1) AS INTEGER
)
FROM categories cat
WHERE products.category_id = cat.category_id
  AND products.root_category_id IS NULL;

-- 2. Индексы
CREATE INDEX IF NOT EXISTS idx_products_root_cat ON products (root_category_id);

CREATE INDEX IF NOT EXISTS idx_orders_date_status ON orders (order_date, status_id)
WHERE status_id IN (2, 3, 4, 5, 6);

CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id, quantity)
INCLUDE (order_id);

-- 3. Таблица агрегатов
CREATE TABLE IF NOT EXISTS monthly_product_sales (
    year_month CHAR(7) NOT NULL,
    product_id INT NOT NULL,
    root_category_id INT NOT NULL,
    total_quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (year_month, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_monthly_sales_month ON monthly_product_sales (year_month);

-- 4. Метаданные для инкрементального обновления
CREATE TABLE IF NOT EXISTS aggregation_metadata (
    job_name TEXT PRIMARY KEY,
    last_processed_order_date TIMESTAMP
);

INSERT INTO aggregation_metadata (job_name, last_processed_order_date)
VALUES ('monthly_sales', '2020-01-01')
ON CONFLICT (job_name) DO NOTHING;