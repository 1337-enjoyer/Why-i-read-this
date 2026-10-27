import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, desc

from app.core.users import current_active_user
from app.models.user import User
from app.models.read_article import ReadArticle
from app.db.session import get_db

router = APIRouter(prefix="/wiki", tags=["wiki"])

WIKI_API = "https://ru.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": (
        "RandomWikiReader/1.0 "
        "(https://github.com/your-repo; your@email.com)"
    )
}


class WikiArticle(BaseModel):
    title: str
    extract: str
    page_id: int
    image_url: str | None = None


class ReadArticleResponse(BaseModel):
    id: str
    page_id: int
    title: str
    read_at: str


def _extract_image_url(page: dict) -> str | None:
    """Достаёт ссылку на миниатюру из ответа API, если она есть."""
    thumbnail = page.get("thumbnail", {})
    return thumbnail.get("source")


async def fetch_random_article_once() -> WikiArticle | None:
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "grnnamespace": "0",
        "grnlimit": "1",
        "prop": "extracts|pageimages",
        "explaintext": True,
        "exsentences": 10,
        "piprop": "thumbnail",
        "pithumbsize": 400,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(WIKI_API, params=params, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    page = next(iter(pages.values()))
    extract = page.get("extract", "")
    if not extract:
        return None

    return WikiArticle(
        title=page.get("title", ""),
        extract=extract,
        page_id=page.get("pageid", 0),
        image_url=_extract_image_url(page),
    )


async def get_random_article_with_retries(
    max_attempts: int = 10,
) -> WikiArticle:
    """Пробует до max_attempts раз, пока не найдёт статью с текстом."""
    for _ in range(max_attempts):
        article = await fetch_random_article_once()
        if article:
            return article
    raise HTTPException(
        502, f"Не удалось найти непустую статью за {max_attempts} попыток"
    )


@router.get("/random", response_model=WikiArticle)
async def get_random_article():
    """Случайная статья без сохранения в историю (для гостей)."""
    return await get_random_article_with_retries()


@router.get("/random/auth", response_model=WikiArticle)
async def get_random_article_auth(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Случайная статья + сохранение в историю пользователя."""
    article = await get_random_article_with_retries()

    record = ReadArticle(
        user_id=user.id,
        page_id=article.page_id,
        title=article.title,
    )
    db.add(record)
    await db.commit()

    return article


@router.get("/history", response_model=list[ReadArticleResponse])
async def get_history(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Список прочитанных статей текущего пользователя (новые сверху)."""
    result = await db.execute(
        select(ReadArticle)
        .where(ReadArticle.user_id == user.id)
        .order_by(desc(ReadArticle.read_at))
    )
    articles = result.scalars().all()
    return [
        ReadArticleResponse(
            id=str(a.id),
            page_id=a.page_id,
            title=a.title,
            read_at=a.read_at.isoformat(),
        )
        for a in articles
    ]


@router.get("/article/{page_id}", response_model=WikiArticle)
async def get_article_by_id(page_id: int):
    """Возвращает статью по её page_id (для открытия из истории)."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageimages",
        "explaintext": True,
        "exsentences": 10,
        "piprop": "thumbnail",
        "pithumbsize": 400,
        "pageids": page_id,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(WIKI_API, params=params, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        raise HTTPException(404, "Статья не найдена")

    page = next(iter(pages.values()))
    extract = page.get("extract", "")
    if not extract:
        raise HTTPException(404, "Текст статьи недоступен")

    return WikiArticle(
        title=page.get("title", ""),
        extract=extract,
        page_id=page_id,
        image_url=_extract_image_url(page),
    )

@router.delete("/history", status_code=204)
async def clear_history(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаляет всю историю прочитанных статей текущего пользователя."""
    await db.execute(
        delete(ReadArticle).where(ReadArticle.user_id == user.id)
    )
    await db.commit()
    return None