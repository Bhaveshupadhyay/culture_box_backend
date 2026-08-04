import pytest
from httpx import AsyncClient
import uuid
from app.core.dependencies import get_storage_provider, get_current_superuser
from app.core.storage.base import StorageProvider
from app.models.user import User
from main import app

class MockStorageProvider(StorageProvider):
    async def upload_file(self, file_content: bytes, file_path: str, content_type: str) -> str:
        return f"https://mock-storage.com/{file_path}"
        
    async def delete_file(self, file_path: str) -> bool:
        return True
        
    async def get_file_url(self, file_path: str) -> str:
        return f"https://mock-storage.com/{file_path}"

async def mock_superuser():
    # Return a dummy superuser
    user = User(id=uuid.uuid4(), email="admin@test.com", is_superuser=True, is_active=True)
    return user

@pytest.fixture
def override_deps():
    app.dependency_overrides[get_storage_provider] = MockStorageProvider
    app.dependency_overrides[get_current_superuser] = mock_superuser
    yield
    app.dependency_overrides.pop(get_storage_provider, None)
    app.dependency_overrides.pop(get_current_superuser, None)

@pytest.mark.asyncio
async def test_media_assets_flow(client: AsyncClient, override_deps):
    # 1. Create a movie
    res = await client.post("/api/v1/movies/", json={
        "title": "Test Movie",
        "original_title": "Test Movie Original",
        "is_active": True
    })
    assert res.status_code == 201
    movie_id = res.json()["id"]

    # 2. Upload a valid media asset (simulate image/png)
    files = {'file': ('poster.png', b'dummy_image_bytes', 'image/png')}
    data = {
        'asset_type': 'poster',
        'title': 'Main Poster',
        'is_primary': 'true'
    }
    res = await client.post(f"/api/v1/movies/{movie_id}/assets", data=data, files=files)
    assert res.status_code == 201
    asset_id = res.json()["id"]
    assert res.json()["url"].startswith("https://mock-storage.com/")

    # 3. Attempt to upload an invalid file type (txt)
    files_bad = {'file': ('bad.txt', b'hello world', 'text/plain')}
    res_bad = await client.post(f"/api/v1/movies/{movie_id}/assets", data=data, files=files_bad)
    assert res_bad.status_code == 400
    assert "not supported" in res_bad.json()["detail"]

    # 4. Get the media assets for the movie
    res_get = await client.get(f"/api/v1/movies/{movie_id}/assets")
    assert res_get.status_code == 200
    assets = res_get.json()
    assert len(assets) == 1
    assert assets[0]["id"] == asset_id

    # 5. Delete the media asset
    res_del = await client.delete(f"/api/v1/movies/assets/{asset_id}")
    assert res_del.status_code == 204

    # Verify it is deleted
    res_get_after = await client.get(f"/api/v1/movies/{movie_id}/assets")
    assert len(res_get_after.json()) == 0
