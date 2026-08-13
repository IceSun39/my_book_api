import pytest
from httpx import AsyncClient


# --- POST (Реєстрація / створення користувача) ---

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """Тест успішного створення (реєстрації) користувача"""
    payload = {
        "email": "new_user@test.com",
        "first_name": "Іван",
        "last_name": "Коваленко",
        "password": "securepassword123"
    }

    response = await async_client.post("/api/users/", json=payload)

    assert response.status_code in [200, 201]
    data = response.json()
    assert data["email"] == "new_user@test.com"
    assert data["first_name"] == "Іван"
    assert data["last_name"] == "Коваленко"
    assert "user_id" in data
    # Перевіряємо, що у відповіді немає захешованого пароля (безпека!)
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_validation_error(async_client: AsyncClient):
    """Тест створення користувача з невалідним email"""
    payload = {
        "email": "not-an-email",
        "first_name": "Тест",
        "last_name": "Тестувальник",
        "password": "123"  # Занадто короткий пароль або інші обмеження схем
    }

    response = await async_client.post("/api/users/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient):
    """Тест перевірки на дублікат email (має повернути 409 Conflict)"""
    payload = {
        "email": "duplicate@test.com",
        "first_name": "Оригінал",
        "last_name": "Тестовий",
        "password": "securepassword123"
    }

    # 1. Успішно створюємо першого користувача
    response_1 = await async_client.post("/api/users/", json=payload)
    assert response_1.status_code in [200, 201]

    # 2. Намагаємось створити другого з тим самим email (можемо змінити ім'я, головне — email)
    payload_duplicate = {
        "email": "duplicate@test.com",
        "first_name": "Клон",
        "last_name": "Тестовий",
        "password": "anotherpassword321"
    }
    response_2 = await async_client.post("/api/users/", json=payload_duplicate)

    # Очікуємо статус 409 Conflict
    assert response_2.status_code == 409
    assert "already exists" in response_2.json()["detail"].lower()

# --- GET (Отримання користувачів) ---

@pytest.mark.asyncio
async def test_get_all_users(async_client: AsyncClient):
    """Тест отримання списку всіх користувачів"""
    # Створюємо користувача
    await async_client.post("/api/users/", json={
        "email": "list_user@test.com",
        "first_name": "Олена",
        "last_name": "Петрівна",
        "password": "password123"
    })

    response = await async_client.get("/api/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient):
    """Тест отримання конкретного користувача за його ID"""
    create_res = await async_client.post("/api/users/", json={
        "email": "specific_user@test.com",
        "first_name": "Петро",
        "last_name": "Сидоренко",
        "password": "password123"
    })
    user_id = create_res.json()["user_id"]

    response = await async_client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == "specific_user@test.com"


@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient):
    """Тест отримання неіснуючого користувача (має бути 404)"""
    response = await async_client.get("/api/users/9999")
    assert response.status_code == 404


# --- PUT (Оновлення користувача) ---

@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient):
    """Тест успішного оновлення даних користувача"""
    create_res = await async_client.post("/api/users/", json={
        "email": "update_me@test.com",
        "first_name": "СтареІм'я",
        "last_name": "Прізвище",
        "password": "password123"
    })
    user_id = create_res.json()["user_id"]

    update_payload = {
        "first_name": "НовеІм'я"
    }

    response = await async_client.put(f"/api/users/{user_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["first_name"] == "НовеІм'я"
    assert response.json()["last_name"] == "Прізвище"  # Перевіряємо, що інші поля не затерлися (exclude_unset)


# --- DELETE (Видалення користувача) ---

@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient):
    """Тест успішного видалення користувача"""
    create_res = await async_client.post("/api/users/", json={
        "email": "delete_user@test.com",
        "first_name": "Дмитро",
        "last_name": "Видалений",
        "password": "password123"
    })
    user_id = create_res.json()["user_id"]

    delete_res = await async_client.delete(f"/api/users/{user_id}")
    assert delete_res.status_code == 204

    get_res = await async_client.get(f"/api/users/{user_id}")
    assert get_res.status_code == 404