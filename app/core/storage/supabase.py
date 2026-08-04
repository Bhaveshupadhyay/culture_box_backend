import httpx
from app.core.config import settings
from app.core.storage.base import StorageProvider
from fastapi import HTTPException, status

class SupabaseStorageProvider(StorageProvider):
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket = "media"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
            
        # The Supabase Storage API endpoint
        self.base_url = f"{self.supabase_url}/storage/v1/object"
        self.headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key
        }

    async def upload_file(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """
        Uploads a file to Supabase Storage using its REST API.
        """
        url = f"{self.base_url}/{self.bucket}/{file_path}"
        headers = self.headers.copy()
        headers["Content-Type"] = content_type
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, content=file_content, headers=headers)
            
            if response.status_code not in (200, 201):
                # If file exists, Supabase returns 400 or 409 usually, we could try UPSERT by adding x-upsert header
                # Let's try upsert if it fails, or just throw
                headers["x-upsert"] = "true"
                response = await client.post(url, content=file_content, headers=headers)
                if response.status_code not in (200, 201):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to upload to Supabase: {response.text}"
                    )
                    
        return await self.get_file_url(file_path)

    async def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file from Supabase Storage.
        """
        url = f"{self.base_url}/{self.bucket}/{file_path}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            return response.status_code in (200, 204)

    async def get_file_url(self, file_path: str) -> str:
        """
        Returns the public URL for a given file path in Supabase Storage.
        Assumes the bucket is public.
        """
        return f"{self.base_url}/public/{self.bucket}/{file_path}"
