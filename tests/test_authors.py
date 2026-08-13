import pytest
from httpx import AsyncClient


# --- POST (Створення) ---

@pytest.mark.asyncio
async def test_create_author(async_client: AsyncClient):
    """Тест успішного створення автора без книг"""
    payload = {
        "fullname": "Іван Франко",
        "email": "ivan.franko@test.com",
        "book_ids": []
    }

    response = await async_client.post("/api/authors/", json=payload)

    # Залежно від налаштувань роутера, FastAPI може повертати 200 або 201
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["fullname"] == "Іван Франко"
    assert data["email"] == "ivan.franko@test.com"
    assert "author_id" in data
    assert data["books"] == []


@pytest.mark.asyncio
async def test_create_author_validation_error(async_client: AsyncClient):
    """Тест створення автора з невалідними даними (наприклад, порожнє ім'я)"""
    payload = {
        "fullname": "",
        "email": "invalid_email",
        "book_ids": []
    }

    response = await async_client.post("/api/authors/", json=payload)

    assert response.status_code == 422  # Unprocessable Entity (Помилка валідації Pydantic)


@pytest.mark.asyncio
async def test_create_author_invalid_books(async_client: AsyncClient):
    """Тест створення автора з неіснуючими книгами"""
    payload = {
        "fullname": "Леся Українка",
        "email": "lesya@test.com",
        "book_ids": [9999]  # Книги з таким ID не існує
    }

    response = await async_client.post("/api/authors/", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Books not found"


# --- GET (Отримання) ---

@pytest.mark.asyncio
async def test_get_all_authors(async_client: AsyncClient):
    """Тест отримання списку всіх авторів"""
    # Спочатку створюємо автора, щоб список не був порожнім
    await async_client.post("/api/authors/", json={
        "fullname": "Ліна Костенко",
        "email": "lina@test.com",
        "book_ids": []
    })

    response = await async_client.get("/api/authors/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["fullname"] == "Ліна Костенко"


@pytest.mark.asyncio
async def test_get_author_by_id(async_client: AsyncClient):
    """Тест отримання конкретного автора за ID"""
    # 1. Створюємо
    create_response = await async_client.post("/api/authors/", json={
        "fullname": "Григорій Сковорода",
        "email": "skovoroda@test.com",
        "book_ids": []
    })
    author_id = create_response.json()["author_id"]

    # 2. Отримуємо
    response = await async_client.get(f"/api/authors/{author_id}")

    assert response.status_code == 200
    assert response.json()["fullname"] == "Григорій Сковорода"


@pytest.mark.asyncio
async def test_get_author_not_found(async_client: AsyncClient):
    """Тест отримання неіснуючого автора"""
    response = await async_client.get("/api/authors/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def  test_get_all_author_books(async_client: AsyncClient):
    """Тест отримання всіх книг автора"""
    # 1. Створюємо
    create_response = await async_client.post("/api/authors/", json={
        "fullname": "Григорій Сковорода",
        "email": "skovoroda@test.com",
        "book_ids": []
    })
    author_id = create_response.json()["author_id"]
    response = await async_client.get(f"/api/authors/{author_id}/books")

    assert response.status_code == 200
    assert response.json() == []

# --- PUT (Оновлення) ---

@pytest.mark.asyncio
async def test_update_author(async_client: AsyncClient):
    """Тест успішного оновлення даних автора"""
    # 1. Створюємо
    create_response = await async_client.post("/api/authors/", json={
        "fullname": "Старе Ім'я",
        "email": "old@test.com",
        "book_ids": []
    })
    author_id = create_response.json()["author_id"]

    # 2. Оновлюємо
    update_payload = {
        "fullname": "Нове Ім'я",
        "email": "new@test.com",
        "book_ids": []
    }
    update_response = await async_client.put(f"/api/authors/{author_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["fullname"] == "Нове Ім'я"
    assert update_response.json()["email"] == "new@test.com"


# --- DELETE (Видалення) ---

@pytest.mark.asyncio
async def test_delete_author(async_client: AsyncClient):
    """Тест успішного видалення автора"""
    # 1. Створюємо
    create_response = await async_client.post("/api/authors/", json={
        "fullname": "Автор Для Видалення",
        "email": "delete_me@test.com",
        "book_ids": []
    })
    author_id = create_response.json()["author_id"]

    # 2. Видаляємо
    delete_response = await async_client.delete(f"/api/authors/{author_id}")

    assert delete_response.status_code == 204  # Очікуємо No Content

    # 3. Перевіряємо, що його більше немає в базі
    get_response = await async_client.get(f"/api/authors/{author_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_author_not_found(async_client: AsyncClient):
    """Тест видалення неіснуючого автора"""
    response = await async_client.delete("/api/authors/9999")

    # Якщо твій роутер кидає 404 при видаленні неіснуючого
    assert response.status_code == 404