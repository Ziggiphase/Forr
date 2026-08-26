"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Cookies from "js-cookie";

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: "", // OAuth2 uses 'username' for email
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const urlEncodedData = new URLSearchParams();
      urlEncodedData.append("username", formData.username);
      urlEncodedData.append("password", formData.password);

      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: urlEncodedData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await res.json();
      
      // Store token in cookie
      Cookies.set("access_token", data.access_token, { expires: 1, path: '/' });
      
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "60px auto", padding: "20px", fontFamily: "sans-serif" }}>
      <h2>Login to Forr</h2>
      {error && <div style={{ color: "red", marginBottom: "15px" }}>{error}</div>}
      
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        <input name="username" type="email" placeholder="Email Address" required value={formData.username} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="password" type="password" placeholder="Password" required value={formData.password} onChange={handleChange} style={{ padding: "10px" }} />
        
        <button type="submit" disabled={loading} style={{ padding: "12px", background: "blue", color: "white", border: "none", cursor: "pointer", fontWeight: "bold" }}>
          {loading ? "Logging in..." : "Log In"}
        </button>
      </form>

      <p style={{ marginTop: "20px", textAlign: "center" }}>
        Don't have an account? <Link href="/signup" style={{ color: "blue", textDecoration: "none" }}>Sign up</Link>
      </p>
    </div>
  );
}
