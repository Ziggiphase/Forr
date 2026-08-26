import asyncio
import httpx

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login with the test user we created earlier
        login_data = {
            "username": "testuser@forr.com",
            "password": "securepassword123"
        }
        res = await client.post("/api/v1/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        access_token = res.json()["access_token"]
        print("Login successful")

        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Create Business
        business_payload = {
            "name": "Test Business LLC",
            "business_type": "Tech",
            "description": "A cool tech business.",
            "integration_types": ["Facebook", "WhatsApp"],
            "address": "456 Tech Avenue",
            "size": "11-50",
            "service_mode": "both"
        }
        res = await client.post("/api/v1/businesses/", json=business_payload, headers=headers)
        assert res.status_code == 201, f"Business creation failed: {res.text}"
        created_business = res.json()
        print("Business created successfully:", created_business["name"])
        business_id = created_business["id"]

        # 3. List Businesses
        res = await client.get("/api/v1/businesses/", headers=headers)
        assert res.status_code == 200, f"List failed: {res.text}"
        businesses = res.json()
        assert len(businesses) >= 1
        assert any(b["id"] == business_id for b in businesses)
        print(f"Business list retrieved successfully, count: {len(businesses)}")

        # 4. Get Single Business
        res = await client.get(f"/api/v1/businesses/{business_id}", headers=headers)
        assert res.status_code == 200, f"Single fetch failed: {res.text}"
        business = res.json()
        assert business["name"] == "Test Business LLC"
        print("Single business fetched successfully!")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
