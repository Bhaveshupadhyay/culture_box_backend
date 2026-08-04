import asyncio
import uuid
import httpx
from sqlalchemy.future import select
from app.core.client import get_postgres_client
from app.models.user import User
from app.models.movie import Movie, MediaAsset
from app.core.storage.supabase import SupabaseStorageProvider

async def test_prod_flow():
    print("Testing Prod Flow for Media Assets without dropping tables...")
    
    # 1. Get a superuser
    session_maker = get_postgres_client()
    async with session_maker() as session:
        stmt = select(User).where(User.is_superuser == True)
        result = await session.execute(stmt)
        superuser = result.scalars().first()
        
        if not superuser:
            print("❌ No superuser found in prod DB. Please run create_superuser.py first.")
            return

        print(f"✅ Found superuser: {superuser.email}")

        # 2. Create a dummy movie
        new_movie = Movie(
            title="Prod Test Movie",
            original_title="Prod Test Movie",
            is_active=False
        )
        session.add(new_movie)
        await session.commit()
        await session.refresh(new_movie)
        print(f"✅ Created dummy movie with ID: {new_movie.id}")
        movie_id = new_movie.id
        
        # 3. Test Supabase Upload Directly (Since we don't have a token to hit our own API easily in a script)
        # We will test the StorageProvider
        try:
            storage = SupabaseStorageProvider()
            
            # Create a dummy image
            dummy_image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            
            file_path = f"movies/{movie_id}/poster/test_upload.png"
            print(f"Uploading file to Supabase: {file_path}")
            
            url = await storage.upload_file(
                file_content=dummy_image_content,
                file_path=file_path,
                content_type="image/png"
            )
            print(f"✅ Successfully uploaded! URL: {url}")
            
            # 4. Save to DB
            asset = MediaAsset(
                movie_id=movie_id,
                asset_type="poster",
                file_path=file_path,
                url=url,
                title="Test Poster",
                is_primary=True
            )
            session.add(asset)
            await session.commit()
            await session.refresh(asset)
            asset_id = asset.id
            print(f"✅ Successfully saved asset to Prod DB! ID: {asset_id}")
            
            # 5. Cleanup
            print("Cleaning up test data from Supabase...")
            deleted = await storage.delete_file(file_path)
            if deleted:
                print("✅ Successfully deleted file from Supabase!")
            else:
                print("❌ Failed to delete file from Supabase!")
                
        except Exception as e:
            print(f"❌ Error during Supabase test: {str(e)}")
            
        finally:
            print("Cleaning up dummy movie from Prod DB...")
            # Deleting the movie will cascade delete the MediaAsset row
            await session.delete(new_movie)
            await session.commit()
            print("✅ Successfully cleaned up Prod DB!")

if __name__ == "__main__":
    asyncio.run(test_prod_flow())
