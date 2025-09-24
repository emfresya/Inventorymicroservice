import os
import logging
import psycopg2
from app.celery_app import celery_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'testcase'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

@celery_app.task(bind=True, max_retries=3)
def update_monthly_sales_task(self):
    logger.info("Запуск задачи обновления monthly_product_sales...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        with open('/scripts/update_monthly_sales.sql', 'r') as f:
            cursor.execute(f.read())
        conn.commit()
        logger.info("Агрегаты успешно обновлены")
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        if conn:
            conn.close()