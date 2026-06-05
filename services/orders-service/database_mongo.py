from motor.motor_asyncio import AsyncIOMotorClient
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://orders-db:27017/orders_db")

client = AsyncIOMotorClient(DATABASE_URL)
db = client.get_default_database()


def get_orders_collection():
    return db["orders"]
