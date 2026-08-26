"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    nin: "",
    dob: "",
    nationality: "Nigerian",
    gender: "Male",
    state: "",
    address: "",
    phone_number: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Signup failed");
      }

      alert("Signup successful! Please check your email/console to verify your account.");
      router.push("/login");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "40px auto", padding: "20px", fontFamily: "sans-serif" }}>
      <h2>Create your Forr Account</h2>
      {error && <div style={{ color: "red", marginBottom: "15px" }}>{error}</div>}
      
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        <input name="name" placeholder="Full Name" required value={formData.name} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="email" type="email" placeholder="Email Address" required value={formData.email} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="password" type="password" placeholder="Password (min 8 chars)" required minLength={8} value={formData.password} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="nin" placeholder="NIN (Optional)" value={formData.nin} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="dob" type="date" required value={formData.dob} onChange={handleChange} style={{ padding: "10px" }} title="Date of Birth" />
        
        <select name="nationality" value={formData.nationality} onChange={handleChange} style={{ padding: "10px" }}>
          <option value="Nigerian">Nigerian</option>
          <option value="Other">Other</option>
        </select>
        
        <select name="gender" value={formData.gender} onChange={handleChange} style={{ padding: "10px" }}>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
        
        <input name="state" placeholder="State" required value={formData.state} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="address" placeholder="Address" required value={formData.address} onChange={handleChange} style={{ padding: "10px" }} />
        <input name="phone_number" placeholder="Phone Number" required value={formData.phone_number} onChange={handleChange} style={{ padding: "10px" }} />
        
        <button type="submit" disabled={loading} style={{ padding: "12px", background: "blue", color: "white", border: "none", cursor: "pointer", fontWeight: "bold" }}>
          {loading ? "Signing up..." : "Sign Up"}
        </button>
      </form>

      <p style={{ marginTop: "20px", textAlign: "center" }}>
        Already have an account? <Link href="/login" style={{ color: "blue", textDecoration: "none" }}>Log in</Link>
      </p>
    </div>
  );
}
