from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert
from sqlalchemy.exc import IntegrityError
from app.database import orders, products, order_items, get_db, monthly_product_sales, products, categories
from app.cache import get_top5_from_cache, set_top5_to_cache
from app.schemas import OrderItemCreate, OrderItemResponse
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/{order_id}/items", response_model=OrderItemResponse)
def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    # 1. Проверяем заказ
    order_query = select(orders.c.status_id).where(orders.c.order_id == order_id)
    order = db.execute(order_query).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.status_id != 1:
        raise HTTPException(status_code=400, detail="Нельзя изменять подтверждённый заказ")

    # 2. Проверяем товар
    product_query = select(products.c.quantity, products.c.price).where(products.c.product_id == item.product_id)
    product = db.execute(product_query).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if product.quantity < item.quantity:
        raise HTTPException(status_code=400, detail=f"Недостаточно товара на складе. Доступно: {product.quantity}")

    # 3. Проверяем существующую позицию
    existing_query = (
        select(order_items.c.order_item_id, order_items.c.quantity)
        .where(order_items.c.order_id == order_id)
        .where(order_items.c.product_id == item.product_id)
    )
    existing = db.execute(existing_query).first()

    if existing:
        # Обновляем количество
        new_quantity = existing.quantity + item.quantity
        stmt = (
            update(order_items)
            .where(order_items.c.order_item_id == existing.order_item_id)
            .values(quantity=new_quantity)
        )
        db.execute(stmt)
        db.commit()
        return OrderItemResponse(
            order_item_id=existing.order_item_id,
            order_id=order_id,
            product_id=item.product_id,
            quantity=new_quantity,
            price_at_order=float(product.price)
        )
    else:
        # Создаём новую позицию
        stmt = (
            insert(order_items)
            .values(
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_order=product.price
            )
            .returning(order_items.c.order_item_id)
        )
        result = db.execute(stmt)
        order_item_id = result.scalar_one()
        db.commit()
        return OrderItemResponse(
            order_item_id=order_item_id,
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_order=float(product.price)
        )

@router.get("/top5")
def get_top5_products(db: Session = Depends(get_db)):
    # 1. Проверяем кэш
    cached = get_top5_from_cache()
    if cached:
        return cached

    # 2. Запрос к агрегатам
    query = (
        select(
            products.c.name,
            categories.c.name.label("category"),
            monthly_product_sales.c.total_quantity
        )
        .select_from(monthly_product_sales)
        .join(products, monthly_product_sales.c.product_id == products.c.product_id)
        .join(categories, monthly_product_sales.c.root_category_id == categories.c.category_id)
        .where(monthly_product_sales.c.year_month == datetime.now().strftime('%Y-%m'))
        .order_by(monthly_product_sales.c.total_quantity.desc())
        .limit(5)
    )
    result = db.execute(query).fetchall()
    
    # 3. Преобразуем в список словарей
    data = [
        {
            "Наименование товара": row.name,
            "Категория 1-го уровня": row.category,
            "Общее количество проданных штук": row.total_quantity
        }
        for row in result
    ]
    
    # 4. Сохраняем в кэш
    set_top5_to_cache(data)
    return data