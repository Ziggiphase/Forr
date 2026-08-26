import asyncio
import httpx

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Signup
        signup_data = {
            "name": "Test User",
            "email": "testuser@forr.com",
            "password": "securepassword123",
            "nin": "12345678901",
            "dob": "1990-01-01",
            "nationality": "Nigerian",
            "gender": "Male",
            "state": "Lagos",
            "address": "123 Test Street",
            "phone_number": "08012345678"
        }
        res = await client.post("/api/v1/auth/signup", json=signup_data)
        if res.status_code == 400 and "already registered" in res.text:
            print("User already exists, skipping signup")
        else:
            assert res.status_code == 201, f"Signup failed: {res.text}"
            print("Signup successful")

        # Get the verify token from the DB to verify email
        import psycopg
        async with await psycopg.AsyncConnection.connect("postgresql://forr:forr_dev@localhost:5432/forr_db") as aconn:
            async with aconn.cursor() as acur:
                await acur.execute("SELECT id FROM users WHERE email = %s", ("testuser@forr.com",))
                user_record = await acur.fetchone()
                token = str(user_record[0])


        # 2. Verify Email
        res = await client.get(f"/api/v1/auth/verify-email?token={token}")
        assert res.status_code == 200, f"Verify failed: {res.text}"
        print("Verify successful")

        # 3. Login
        login_data = {
            "username": "testuser@forr.com",
            "password": "securepassword123"
        }
        res = await client.post("/api/v1/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        access_token = res.json()["access_token"]
        print("Login successful")

        # 4. Get Profile
        res = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert res.status_code == 200, f"Profile fetch failed: {res.text}"
        profile = res.json()
        assert profile["name"] == "Test User"
        assert profile["email"] == "testuser@forr.com"
        print("Profile fetched successfully and matches:")
        print(profile)

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
