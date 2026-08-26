"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Cookies from "js-cookie";

export default function DashboardHomePage() {
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBusinesses = async () => {
      const token = Cookies.get("access_token");
      try {
        const res = await fetch("/api/v1/businesses", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setBusinesses(data);
        }
      } catch (err) {
        console.error("Failed to fetch businesses", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBusinesses();
  }, []);

  if (loading) return <div>Loading businesses...</div>;

  return (
    <div style={{ fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1>Your Businesses</h1>
        <Link 
          href="/dashboard/businesses/new" 
          style={{ padding: "10px 20px", background: "blue", color: "white", textDecoration: "none", borderRadius: "4px", fontWeight: "bold" }}
        >
          Create your business
        </Link>
      </div>

      {businesses.length === 0 ? (
        <div style={{ textAlign: "center", padding: "50px", background: "#f9f9f9", borderRadius: "8px", border: "1px dashed #ccc" }}>
          <h3>No businesses yet</h3>
          <p style={{ color: "#666", marginBottom: "20px" }}>Register your first business to get started.</p>
          <Link 
            href="/dashboard/businesses/new" 
            style={{ padding: "10px 20px", background: "blue", color: "white", textDecoration: "none", borderRadius: "4px", fontWeight: "bold" }}
          >
            Create your business
          </Link>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
          {businesses.map((biz) => (
            <Link 
              key={biz.id} 
              href={`/dashboard/businesses/${biz.id}`} 
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "20px", background: "white", boxShadow: "0 2px 4px rgba(0,0,0,0.05)", cursor: "pointer" }}>
                <h3 style={{ marginTop: 0 }}>{biz.name}</h3>
                <p style={{ color: "#555", fontSize: "14px" }}><strong>Type:</strong> {biz.business_type}</p>
                <p style={{ color: "#555", fontSize: "14px" }}><strong>Size:</strong> {biz.size}</p>
                <p style={{ color: "#777", fontSize: "14px", marginTop: "10px", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
                  {biz.description || "No description provided"}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
