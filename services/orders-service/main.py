from fastapi import FastAPI, APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
import httpx
import os

from database_mongo import get_orders_collection
from models import (
    OrderCreate, OrderRead, OrderStatusUpdate,
    OrderItem, OrderStatus
)

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8002")

app = FastAPI(title="EmmaPaws — Órdenes de Compra")
router = APIRouter()


def serialize_order(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/")
def read_root():
    return {"message": "Servicio de Órdenes de EmmaPaws funcionando."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/orders/", response_model=List[OrderRead])
async def get_orders():
    collection = get_orders_collection()
    orders = await collection.find().to_list(length=100)
    return [serialize_order(o) for o in orders]


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(order_id: str):
    collection = get_orders_collection()
    try:
        oid = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de orden inválido")
    order = await collection.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return serialize_order(order)


@router.post("/orders/", response_model=OrderRead, status_code=201)
async def create_order(order: OrderCreate):
    collection = get_orders_collection()
    resolved_items = []
    total = 0.0

    async with httpx.AsyncClient() as client:
        for item_req in order.items:
            try:
                resp = await client.get(
                    f"{CATALOG_SERVICE_URL}/api/v1/products/{item_req.product_id}"
                )
                resp.raise_for_status()
                product = resp.json()
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item_req.product_id} no encontrado en catálogo"
                )

            unit_price = product["price"]
            resolved_items.append(OrderItem(
                product_id=item_req.product_id,
                product_name=product["name"],
                quantity=item_req.quantity,
                unit_price=unit_price,
            ).model_dump())
            total += unit_price * item_req.quantity

    doc = {
        "user_email": order.user_email,
        "items": resolved_items,
        "total": round(total, 2),
        "status": OrderStatus.pending,
        "created_at": datetime.utcnow(),
    }
    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_order(doc)


@router.put("/orders/{order_id}/status", response_model=OrderRead)
async def update_order_status(order_id: str, body: OrderStatusUpdate):
    collection = get_orders_collection()
    try:
        oid = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de orden inválido")
    result = await collection.find_one_and_update(
        {"_id": oid},
        {"$set": {"status": body.status}},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return serialize_order(result)


app.include_router(router, prefix="/api/v1")
