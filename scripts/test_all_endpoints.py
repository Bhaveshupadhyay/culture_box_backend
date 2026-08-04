import asyncio
import httpx
from sqlalchemy.future import select
from main import app
from app.core.client import get_postgres_client
from app.models.user import User
from app.core.security import get_password_hash
import uuid

async def test_endpoints():
    print("Testing all endpoints...")
    
    # 1. Create a test superuser directly in DB
    session_maker = get_postgres_client()
    test_email = f"test_super_{uuid.uuid4()}@example.com"
    test_password = "password123"
    
    async with session_maker() as session:
        new_user = User(
            email=test_email,
            hashed_password=get_password_hash(test_password),
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        user_id = new_user.id
        print(f"Created test superuser: {test_email}")

    created_movie_ids = []
    created_genre_ids = []
    created_person_ids = []

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Login
            response = await client.post(
                "/api/v1/auth/login",
                data={"username": test_email, "password": test_password}
            )
            assert response.status_code == 200, f"Login failed: {response.text}"
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful")
            
            # Create Genre
            response = await client.post(
                "/api/v1/genres/",
                json={"name": f"Test Genre {uuid.uuid4()}"},
                headers=headers
            )
            assert response.status_code == 201, f"Genre creation failed: {response.text}"
            genre_id = response.json()["id"]
            created_genre_ids.append(genre_id)
            print(f"Created genre: {genre_id}")
            
            # Get Genres
            response = await client.get("/api/v1/genres/")
            assert response.status_code == 200, "Get genres failed"
            print("Get genres successful")
            
            # Create Person
            response = await client.post(
                "/api/v1/people/",
                json={"name": "Test Person", "biography": "Test Bio"},
                headers=headers
            )
            assert response.status_code == 201, f"Person creation failed: {response.text}"
            person_id = response.json()["id"]
            created_person_ids.append(person_id)
            print(f"Created person: {person_id}")
            
            # Create Movie
            response = await client.post(
                "/api/v1/movies/",
                json={
                    "title": "Test Movie Endpoints",
                    "original_title": "Test Movie Endpoints Original",
                    "is_active": True,
                    "genre_ids": [genre_id]
                },
                headers=headers
            )
            assert response.status_code == 201, f"Movie creation failed: {response.text}"
            movie_id = response.json()["id"]
            created_movie_ids.append(movie_id)
            print(f"Created movie: {movie_id}")
            
            # Add Cast
            response = await client.post(
                f"/api/v1/movies/{movie_id}/cast",
                json={
                    "person_id": person_id,
                    "character": "Main Character",
                    "order": 1
                },
                headers=headers
            )
            assert response.status_code == 200, f"Add cast failed: {response.text}"
            print("Added cast member")
            
            # Add Crew
            response = await client.post(
                f"/api/v1/movies/{movie_id}/crew",
                json={
                    "person_id": person_id,
                    "job": "Director",
                    "department": "Directing"
                },
                headers=headers
            )
            assert response.status_code == 200, f"Add crew failed: {response.text}"
            print("Added crew member")
            
            # Get Movies
            response = await client.get("/api/v1/movies/")
            assert response.status_code == 200, "Get movies failed"
            print("Get movies successful")
            
            # Homepage
            response = await client.get("/api/v1/homepage/layout")
            assert response.status_code == 200, f"Homepage failed: {response.text}"
            print("Get homepage successful")
            
            print("All endpoints checked successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")

    finally:
        # Cleanup
        print("Cleaning up inserted data...")
        async with session_maker() as session:
            from app.models.movie import Movie, Genre, Person, MovieCast, MovieCrew
            for m_id in created_movie_ids:
                stmt = select(MovieCast).where(MovieCast.movie_id == m_id)
                res = await session.execute(stmt)
                for cast in res.scalars().all():
                    await session.delete(cast)
                    
                stmt = select(MovieCrew).where(MovieCrew.movie_id == m_id)
                res = await session.execute(stmt)
                for crew in res.scalars().all():
                    await session.delete(crew)

                stmt = select(Movie).where(Movie.id == m_id)
                res = await session.execute(stmt)
                m = res.scalars().first()
                if m:
                    await session.delete(m)
                    
            for g_id in created_genre_ids:
                stmt = select(Genre).where(Genre.id == g_id)
                res = await session.execute(stmt)
                g = res.scalars().first()
                if g:
                    await session.delete(g)
                    
            for p_id in created_person_ids:
                stmt = select(Person).where(Person.id == p_id)
                res = await session.execute(stmt)
                p = res.scalars().first()
                if p:
                    await session.delete(p)

            # Delete the test superuser
            stmt = select(User).where(User.id == user_id)
            res = await session.execute(stmt)
            u = res.scalars().first()
            if u:
                await session.delete(u)
                
            await session.commit()
            print("Cleanup complete!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
