"""Test MongoDB connection"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        print('Testing connection...')
        result = await client.admin.command('ping')
        print('Connection successful!', result)
        await client.close()
        return True
    except Exception as e:
        print(f'Connection failed: {e}')
        return False

if __name__ == '__main__':
    asyncio.run(test())
