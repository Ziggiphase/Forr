"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

export default function NewBusinessPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    business_type: "",
    description: "",
    address: "",
    size: "1-10",
    service_mode: "physical-only",
  });
  
  const [integrations, setIntegrations] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleIntegrationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (e.target.checked) {
      setIntegrations([...integrations, value]);
    } else {
      setIntegrations(integrations.filter(item => item !== value));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const payload = {
      ...formData,
      integration_types: integrations,
    };

    try {
      const token = Cookies.get("access_token");
      const res = await fetch("/api/v1/businesses", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to create business");
      }

      const newBusiness = await res.json();
      router.push(`/dashboard/businesses/${newBusiness.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px", fontFamily: "sans-serif" }}>
      <h2>Register a New Business</h2>
      {error && <div style={{ color: "red", marginBottom: "15px" }}>{error}</div>}
      
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Business Name</label>
          <input name="name" required value={formData.name} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }} />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Business Type/Industry</label>
          <input name="business_type" placeholder="e.g. Retail, Tech, Food" required value={formData.business_type} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }} />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Description</label>
          <textarea name="description" rows={4} value={formData.description} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }} />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Integration Type (Select all that apply)</label>
          <div style={{ display: "flex", gap: "15px", flexWrap: "wrap" }}>
            {["Facebook", "WhatsApp", "Instagram", "Telegram"].map(platform => (
              <label key={platform} style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <input type="checkbox" value={platform} checked={integrations.includes(platform)} onChange={handleIntegrationChange} />
                {platform}
              </label>
            ))}
          </div>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Business Address</label>
          <input name="address" required value={formData.address} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }} />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Size of Business</label>
          <select name="size" value={formData.size} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }}>
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="200+">200+ employees</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Service Mode</label>
          <select name="service_mode" value={formData.service_mode} onChange={handleChange} style={{ width: "100%", padding: "10px", boxSizing: "border-box" }}>
            <option value="physical-only">Physical only</option>
            <option value="online-remote-only">Online/Remote only</option>
            <option value="both">Both</option>
          </select>
        </div>

        <button type="submit" disabled={loading} style={{ padding: "12px", background: "blue", color: "white", border: "none", cursor: "pointer", fontWeight: "bold", marginTop: "10px", borderRadius: "4px" }}>
          {loading ? "Creating..." : "Create Business"}
        </button>
      </form>
    </div>
  );
}
