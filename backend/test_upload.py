import asyncio
import httpx
import os

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login
        login_data = {
            "username": "testuser@forr.com",
            "password": "securepassword123"
        }
        res = await client.post("/api/v1/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        access_token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("Login successful")

        # 2. Get business ID
        res = await client.get("/api/v1/businesses", headers=headers)
        assert res.status_code == 200
        businesses = res.json()
        assert len(businesses) >= 1
        business_id = businesses[0]["id"]
        print(f"Using business ID: {business_id}")

        # 3. Create dummy CSV
        csv_content = "Gadget,Amount,Details\nLaptop,1500,A fast computer\nPhone,800,A smart phone"
        csv_path = "test_data.csv"
        with open(csv_path, "w") as f:
            f.write(csv_content)

        # 4. Upload and Parse
        with open(csv_path, "rb") as f:
            files = {"file": ("test_data.csv", f, "text/csv")}
            res = await client.post(
                f"/api/v1/businesses/{business_id}/products/upload/parse",
                headers=headers,
                files=files
            )
        assert res.status_code == 200, f"Parse failed: {res.text}"
        parse_data = res.json()
        assert "Gadget" in parse_data["headers"]
        assert len(parse_data["data"]) == 2
        print("File parsed successfully")

        # 5. Send Bulk Request (Mapped)
        mapped_payload = []
        for row in parse_data["data"]:
            mapped_payload.append({
                "name": row["Gadget"],
                "price": float(row["Amount"]),
                "description": row["Details"],
                "quantity": 0,
                "category": "Electronics",
                "status": "draft"
            })
        
        res = await client.post(
            f"/api/v1/businesses/{business_id}/products/bulk",
            headers=headers,
            json=mapped_payload
        )
        assert res.status_code == 201, f"Bulk insert failed: {res.text}"
        print("Bulk insert successful")

        # Cleanup
        os.remove(csv_path)

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
