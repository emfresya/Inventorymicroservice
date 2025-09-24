# fill_test_data.py
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# Подключение к БД
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'testcase')}"
)

engine = create_engine(DATABASE_URL)

# Тестовые данные
categories = [
    ("Электроника", None),
    ("Компьютеры", 1),
    ("Смартфоны", 1),
    ("Телевизоры", 1),
    ("Бытовая техника", None),
    ("Кухня", 5),
    ("Уборка", 5),
]

products_data = [
    "iPhone 15", "Samsung Galaxy S24", "MacBook Pro", "Dell XPS", "iPad Air",
    "PlayStation 5", "Xbox Series X", "AirPods", "Mac Studio", "iPad Pro",
    "Samsung TV", "LG Washing Machine", "Bosch Fridge", "Sony Headphones",
    "Apple Watch", "Nikon Camera", "Canon Printer", "Samsung Tablet",
    "Google Pixel", "Huawei Phone", "LG TV", "Philips Shaver",
    "Dyson Vacuum", "KitchenAid Mixer", "Bosch Cooker", "Nespresso Machine",
    "KitchenAid Blender", "Samsung Fridge", "Apple TV", "Fire TV Stick",
    "Xiaomi Phone", "OnePlus Phone", "Sony TV", "LG Fridge", "Samsung Microwave",
    "Bosch Dishwasher", "Nespresso Coffee", "KitchenAid Toaster", "Dyson Fan",
    "Philips Hair Dryer", "Apple AirTag", "Samsung Watch", "Sony Speaker",
    "JBL Speaker", "Sony Camera", "Canon Camera", "Olympus Camera",
    "GoPro Camera", "Sony Headphones", "Bose Headphones", "Sennheiser Headphones",
    "Apple Magic Mouse", "Logitech Mouse", "Razer Mouse", "Corsair Keyboard",
    "SteelSeries Keyboard", "Razer Keyboard", "ASUS Monitor", "Dell Monitor",
    "LG Monitor", "Samsung Monitor", "Apple Pencil", "Wacom Tablet",
    "Samsung SSD", "WD SSD", "Samsung RAM", "Corsair RAM", "AMD CPU",
    "Intel CPU", "NVIDIA GPU", "AMD GPU", "ASUS Motherboard", "MSI Motherboard",
    "Gigabyte Motherboard", "Thermaltake Case", "Cooler Master Case", "NZXT Case",
    "Deepcool CPU Cooler", "Noctua CPU Cooler", "Corsair PSU", "EVGA PSU",
    "Seasonic PSU", "Samsung HDD", "WD HDD", "Seagate HDD", "Toshiba HDD",
    "Kingston USB", "SanDisk USB", "Samsung USB", "Transcend USB", "Sony USB",
    "Samsung Memory Card", "SanDisk Memory Card", "Lexar Memory Card", "Kingston Memory Card"
]

def fill_db():
    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # 1. Добавляем клиентов
            for i in range(1, 6):
                conn.execute(text("""
                    INSERT INTO clients (name, address) 
                    VALUES (:name, :address)
                    ON CONFLICT DO NOTHING
                """), {
                    "name": f"Клиент {i}",
                    "address": f"Адрес клиента {i}"
                })

            # 2. Добавляем категории (если их нет)
            for i, (name, parent_id) in enumerate(categories, start=1):
                conn.execute(text("""
                    INSERT INTO categories (category_id, name, parent_id, path, level)
                    VALUES (:category_id, :name, :parent_id, :path, :level)
                    ON CONFLICT DO NOTHING
                """), {
                    "category_id": i,
                    "name": name,
                    "parent_id": parent_id,
                    "path": f"/{i}/" if parent_id is None else f"/{parent_id}/{i}/",
                    "level": 0 if parent_id is None else 1
                })

            # 3. Обновляем root_category_id для существующих категорий
            conn.execute(text("""
                UPDATE categories
                SET path = CASE
                    WHEN parent_id IS NULL THEN '/' || category_id || '/'
                    ELSE (SELECT path FROM categories p WHERE p.category_id = categories.parent_id) || category_id || '/'
                END
            """))

            # 4. Добавляем товары
            for i in range(1, 101):
                category_id = random.randint(1, len(categories))
                conn.execute(text("""
                    INSERT INTO products (sku, name, quantity, price, category_id, root_category_id)
                    VALUES (:sku, :name, :quantity, :price, :category_id, :root_category_id)
                    ON CONFLICT DO NOTHING
                """), {
                    "sku": f"SKU-{i:03}",
                    "name": random.choice(products_data),
                    "quantity": random.randint(10, 200),
                    "price": round(random.uniform(1000, 150000), 2),
                    "category_id": category_id,
                    "root_category_id": 1 if category_id in [1, 2, 3, 4] else 5  # корневая категория
                })

            # 5. Создаём заказы
            for i in range(1, 11):
                client_id = random.randint(1, 5)
                status_id = random.choice([2, 3, 4, 5, 6])  # подтверждённые статусы
                total = 0
                order_date = datetime.now() - timedelta(days=random.randint(0, 29))  # текущий месяц

                # Создаём заказ
                result = conn.execute(text("""
                    INSERT INTO orders (client_id, status_id, order_date, total_sum)
                    VALUES (:client_id, :status_id, :order_date, :total_sum)
                    RETURNING order_id
                """), {
                    "client_id": client_id,
                    "status_id": status_id,
                    "order_date": order_date,
                    "total_sum": 0  # посчитаем позже
                })
                order_id = result.fetchone()[0]

                # Добавляем 1–5 позиций в заказ
                num_items = random.randint(1, 5)
                for _ in range(num_items):
                    product_id = random.randint(1, 100)
                    quantity = random.randint(1, 5)
                    price_at_order = round(random.uniform(1000, 100000), 2)
                    total += price_at_order * quantity

                    conn.execute(text("""
                        INSERT INTO order_items (order_id, product_id, quantity, price_at_order)
                        VALUES (:order_id, :product_id, :quantity, :price_at_order)
                    """), {
                        "order_id": order_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "price_at_order": price_at_order
                    })

                # Обновляем total_sum
                conn.execute(text("""
                    UPDATE orders SET total_sum = :total_sum WHERE order_id = :order_id
                """), {"total_sum": total, "order_id": order_id})

            trans.commit()
            print("✅ Тестовые данные успешно добавлены!")

        except Exception as e:
            trans.rollback()
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    fill_db()