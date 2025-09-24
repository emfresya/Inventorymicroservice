import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker

# Подключение
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Метаданные (пустые — мы не создаём таблицы)
metadata = MetaData()

# Описываем существующие таблицы (только нужные колонки)
orders = Table(
    "orders",
    metadata,
    Column("order_id", Integer, primary_key=True),
    Column("client_id", Integer, nullable=False),
    Column("status_id", Integer, nullable=False),
    # остальные колонки не нужны для этого эндпоинта
    autoload_with=engine  # ← автоматически загружает схему из БД!
)

products = Table(
    "products",
    metadata,
    Column("product_id", Integer, primary_key=True),
    Column("quantity", Integer, nullable=False),
    Column("price", Numeric(12, 2), nullable=False),
    autoload_with=engine
)

order_items = Table(
    "order_items",
    metadata,
    Column("order_item_id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("orders.order_id"), nullable=False),
    Column("product_id", Integer, ForeignKey("products.product_id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("price_at_order", Numeric(12, 2), nullable=False),
    autoload_with=engine
)

categories = Table("categories", metadata, autoload_with=engine)

monthly_product_sales = Table("monthly_product_sales", metadata, autoload_with=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()