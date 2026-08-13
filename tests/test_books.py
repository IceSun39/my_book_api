import pytest
from httpx import AsyncClient
from datetime import datetime


# --- Допоміжна фікстура для створення тестового автора, щоб було до чого прив'язувати книги ---
@pytest.fixture
async def sample_author(async_client: AsyncClient):
    response = await async_client.post("/api/authors/", json={
        "fullname": "Тарас Шевченко",
        "email": "shevchenko@test.com",
        "book_ids": []
    })
    return response.json()


# --- POST (Створення книги) ---

@pytest.mark.asyncio
async def test_create_book(async_client: AsyncClient, sample_author):
    """Тест успішного створення книги з існуючим автором"""
    payload = {
        "book_title": "Кобзар",
        "publish_date": "1840-05-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    }

    response = await async_client.post("/api/books/", json=payload)

    assert response.status_code in [200, 201]
    data = response.json()
    assert data["book_title"] == "Кобзар"
    assert "book_id" in data
    assert len(data["authors"]) == 1
    assert data["authors"][0]["fullname"] == "Тарас Шевченко"


@pytest.mark.asyncio
async def test_create_book_author_not_found(async_client: AsyncClient):
    """Тест створення книги з неіснуючим автором (має повернути 404)"""
    payload = {
        "book_title": "Невідома книга",
        "publish_date": "2026-01-01T00:00:00",
        "author_ids": [9999]
    }

    response = await async_client.post("/api/books/", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


# --- GET (Отримання книг) ---

@pytest.mark.asyncio
async def test_get_all_books(async_client: AsyncClient, sample_author):
    """Тест отримання списку всіх книг"""
    # Створюємо книгу
    await async_client.post("/api/books/", json={
        "book_title": "Гайдамаки",
        "publish_date": "1841-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    })

    response = await async_client.get("/api/books/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_book_by_id(async_client: AsyncClient, sample_author):
    """Тест отримання конкретної книги за її ID"""
    create_res = await async_client.post("/api/books/", json={
        "book_title": "Катерина",
        "publish_date": "1838-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    })
    book_id = create_res.json()["book_id"]

    response = await async_client.get(f"/api/books/{book_id}")

    assert response.status_code == 200
    assert response.json()["book_title"] == "Катерина"


@pytest.mark.asyncio
async def test_get_book_not_found(async_client: AsyncClient):
    """Тест отримання неіснуючої книги"""
    response = await async_client.get("/api/books/9999")
    assert response.status_code == 404


# --- PUT (Оновлення книги) ---

@pytest.mark.asyncio
async def test_update_book(async_client: AsyncClient, sample_author):
    """Тест успішного оновлення книги"""
    create_res = await async_client.post("/api/books/", json={
        "book_title": "Стара назва",
        "publish_date": "1850-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    })
    book_id = create_res.json()["book_id"]

    update_payload = {
        "book_title": "Нова назва",
        "publish_date": "1850-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    }

    response = await async_client.put(f"/api/books/{book_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["book_title"] == "Нова назва"


# --- DELETE (Видалення книги) ---

@pytest.mark.asyncio
async def test_delete_book(async_client: AsyncClient, sample_author):
    """Тест успішного видалення книги"""
    create_res = await async_client.post("/api/books/", json={
        "book_title": "Книга на видалення",
        "publish_date": "1860-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    })
    book_id = create_res.json()["book_id"]

    delete_res = await async_client.delete(f"/api/books/{book_id}")
    assert delete_res.status_code == 204

    get_res = await async_client.get(f"/api/books/{book_id}")
    assert get_res.status_code == 404


# --- FAVORITES (Улюблені книги) ---

@pytest.mark.asyncio
async def test_add_and_remove_favorite(async_client: AsyncClient, sample_author):
    """Тест додавання книги в улюблені та її видалення звідти (ідемпотентність)"""
    # 1. Створюємо книгу
    book_res = await async_client.post("/api/books/", json={
        "book_title": "Улюблена книга",
        "publish_date": "1870-01-01T00:00:00",
        "author_ids": [sample_author["author_id"]]
    })
    book_id = book_res.json()["book_id"]

    # 2. Додаємо в улюблені (використовуємо твій роут, шлях залежить від твого book_routes)
    add_res = await async_client.post(f"/api/books/{book_id}/favorite")
    assert add_res.status_code in [200, 201]

    # 3. Перевіряємо, чи з'явилася в списку улюблених
    fav_res = await async_client.get("/api/books/favorite")
    assert fav_res.status_code == 200
    assert len(fav_res.json()) >= 1

    # 4. Видаляємо з улюблених
    remove_res = await async_client.delete(f"/api/books/{book_id}/favorite")
    assert remove_res.status_code in [200, 204]