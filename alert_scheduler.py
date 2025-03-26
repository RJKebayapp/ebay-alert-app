import asyncio
import logging
import requests  # For making eBay API calls; replace with your actual implementation if needed.
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database_config import get_async_session
from models import SavedSearch
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

def get_new_items_for_search(search: SavedSearch):
    """
    Placeholder function to fetch new items from eBay.
    Replace this with your actual API call using your eBay API key.
    """
    # For now, simulate with a dummy list:
    return [{"title": "Sample Item", "price": 100}]

def send_email(to_email: str, subject: str, body: str):
    # Replace with your actual email sending logic.
    logger.info(f"Sending email to {to_email}: {subject}\n{body}")

def send_telegram(message: str):
    # Replace with your actual Telegram notification logic.
    logger.info(f"Sending Telegram message: {message}")

@asynccontextmanager
async def get_session():
    """
    Wrap get_async_session() (which returns an async generator) for use with async with.
    """
    session_gen = get_async_session()
    session = await session_gen.__anext__()
    try:
        yield session
    finally:
        await session_gen.aclose()

async def check_saved_searches():
    """
    Background task that periodically checks saved searches for new items
    and triggers notifications if items are found.
    """
    while True:
        async with get_session() as session:
            # Eagerly load the related user using selectinload
            result = await session.execute(
                select(SavedSearch).options(selectinload(SavedSearch.user))
            )
            searches = result.scalars().all()
            for search in searches:
                new_items = get_new_items_for_search(search)
                if new_items:
                    # With the user eagerly loaded, accessing search.user.email won't trigger lazy-loading.
                    user_email = search.user.email if search.user else "unknown@example.com"
                    subject = f"New items for your search: {search.search_query}"
                    body = f"New items: {new_items}"
                    send_email(user_email, subject, body)
                    send_telegram(f"New items for {search.search_query}: {new_items}")
                    logger.info(f"Alert sent for saved search {search.id} for user {search.user_id}")
                else:
                    logger.info(f"No new items for saved search {search.id} for user {search.user_id}")
        logger.info("Sleeping for 60 seconds before next check...")
        await asyncio.sleep(60)
