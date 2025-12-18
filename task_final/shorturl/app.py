from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from model import URLShortener

app = FastAPI(title="shortURL", version="1.0")

# Инициализация модели
url_model = URLShortener()

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    short_id: str
    short_url: str

class StatsResponse(BaseModel):
    short_id: str
    original_url: str
    created_at: str
    click_count: int

@app.post("/shorten", response_model=URLResponse)
async def shorten_url(request: URLRequest):
    """Создание короткой ссылки"""
    # Валидация URL
    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL должен начинаться с http:// или https://")
    
    # Генерация короткого ID
    short_id = url_model.generate_short_id(request.url)
    
    # Сохранение в БД
    url_model.save_url(request.url, short_id)
    
    # Формирование ответа
    return URLResponse(
        short_id=short_id,
        short_url=f"/{short_id}"
    )

@app.get("/{short_id}")
async def redirect_url(short_id: str):
    """Перенаправление по короткой ссылке"""
    result = url_model.get_url(short_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    original_url, click_count = result
    
    # Увеличиваем счетчик кликов
    url_model.increment_click_count(short_id, click_count)
    
    # Редирект на оригинальный URL
    return RedirectResponse(url=original_url)

@app.get("/stats/{short_id}", response_model=StatsResponse)
async def get_stats(short_id: str):
    """Получение статистики по короткой ссылке"""
    result = url_model.get_stats(short_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    short_id, original_url, created_at, click_count = result
    
    return StatsResponse(
        short_id=short_id,
        original_url=original_url,
        created_at=created_at,
        click_count=click_count
    )

@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "URL Shortener",
        "endpoints": {
            "POST /shorten": "Создать короткую ссылку",
            "GET /{short_id}": "Перейти по короткой ссылке",
            "GET /stats/{short_id}": "Статистика по ссылке"
        }
    }