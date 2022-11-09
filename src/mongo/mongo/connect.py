from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging


async def connect_mongo_client(url: str):
    """Connect to the MongoDB database.

    Args:
        url (str): the connection string to the MongoDB database
    """
    logging.info(f"Connecting to MongoDB {url}...")
    client = AsyncIOMotorClient(url)
    await init_beanie(database=client.db_name, document_models=[])
    logging.info("Connected to MongoDB")