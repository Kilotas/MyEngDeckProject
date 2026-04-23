from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.decks import router as decks_router
from src.api.v1.cards import router as cards_router
from src.api.v1.reviews import router as reviews_router
from src.api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(decks_router)
router.include_router(cards_router)
router.include_router(reviews_router)
router.include_router(users_router)
