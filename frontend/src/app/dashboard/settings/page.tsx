"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form State
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [stateName, setStateName] = useState("");
  const [nationality, setNationality] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      const token = Cookies.get("access_token");
      try {
        const res = await fetch("/api/v1/users/me", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
          setName(data.name || "");
          setPhone(data.phone_number || "");
          setAddress(data.address || "");
          setStateName(data.state || "");
          setNationality(data.nationality || "");
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    const token = Cookies.get("access_token");
    try {
      const res = await fetch("/api/v1/users/me", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          name,
          phone_number: phone,
          address,
          state: stateName,
          nationality
        })
      });
      if (res.ok) {
        setMessage("Profile updated successfully!");
        window.location.reload(); // Simple way to refresh layout user data
      } else {
        const err = await res.json();
        setMessage(`Error: ${err.detail || "Failed to update"}`);
      }
    } catch (err) {
      setMessage("Network error occurred.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div>
      <h1 style={{ margin: "0 0 20px 0" }}>Global Settings</h1>
      
      <div style={{ background: "white", padding: "30px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", maxWidth: "600px", marginBottom: "40px" }}>
        <h2 style={{ marginTop: 0 }}>My Profile</h2>
        {message && <div style={{ padding: "10px", background: message.includes("Error") ? "#ffebee" : "#e8f5e9", color: message.includes("Error") ? "red" : "green", marginBottom: "20px", borderRadius: "4px" }}>{message}</div>}
        
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <div>
            <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Full Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #ccc", borderRadius: "4px" }} required />
          </div>
          <div>
            <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Phone Number</label>
            <input type="text" value={phone} onChange={e => setPhone(e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #ccc", borderRadius: "4px" }} required />
          </div>
          <div>
            <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Address</label>
            <input type="text" value={address} onChange={e => setAddress(e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #ccc", borderRadius: "4px" }} required />
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>State</label>
              <input type="text" value={stateName} onChange={e => setStateName(e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #ccc", borderRadius: "4px" }} required />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Nationality</label>
              <input type="text" value={nationality} onChange={e => setNationality(e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #ccc", borderRadius: "4px" }} required />
            </div>
          </div>
          <button type="submit" disabled={saving} style={{ background: "black", color: "white", padding: "12px", borderRadius: "4px", border: "none", cursor: "pointer", fontWeight: "bold", marginTop: "10px" }}>
            {saving ? "Saving..." : "Save Profile Changes"}
          </button>
        </form>
      </div>

      <div style={{ padding: "20px", background: "#f0f8ff", border: "1px solid #add8e6", borderRadius: "8px", maxWidth: "600px" }}>
        <h3 style={{ marginTop: 0 }}>Looking for Telegram / WhatsApp Integration?</h3>
        <p>Because each business has its own AI agent, you must configure platform integrations inside the specific business dashboard.</p>
        <ol style={{ marginBottom: 0 }}>
          <li>Go to <strong>Businesses</strong> in the sidebar.</li>
          <li>Click on your specific business.</li>
          <li>Click the <strong>Business Integrations & Settings</strong> tab.</li>
        </ol>
      </div>
    </div>
  );
}
