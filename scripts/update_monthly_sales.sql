-- Создаём временную таблицу с новыми заказами
CREATE TEMP TABLE temp_new_orders AS
SELECT 
    oi.product_id,
    p.root_category_id,
    oi.quantity,
    o.order_date
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE 
    o.order_date > (
        SELECT COALESCE(last_processed_order_date, '2020-01-01')
        FROM aggregation_metadata 
        WHERE job_name = 'monthly_sales'
    )
    AND o.status_id IN (2, 3, 4, 5, 6)
    AND p.root_category_id IS NOT NULL;

-- Если новых заказов нет — выходим
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM temp_new_orders) THEN
        RETURN;
    END IF;

    -- Агрегируем и обновляем monthly_product_sales
    INSERT INTO monthly_product_sales (year_month, product_id, root_category_id, total_quantity)
    SELECT
        to_char(order_date, 'YYYY-MM'),
        product_id,
        root_category_id,
        SUM(quantity)
    FROM temp_new_orders
    GROUP BY to_char(order_date, 'YYYY-MM'), product_id, root_category_id
    ON CONFLICT (year_month, product_id)
    DO UPDATE SET
        total_quantity = monthly_product_sales.total_quantity + EXCLUDED.total_quantity,
        last_updated = CURRENT_TIMESTAMP;

    -- Обновляем метаданные
    UPDATE aggregation_metadata
    SET last_processed_order_date = (SELECT MAX(order_date) FROM temp_new_orders)
    WHERE job_name = 'monthly_sales';
END $$;