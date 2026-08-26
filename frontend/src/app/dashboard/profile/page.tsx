"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      const token = Cookies.get("access_token");
      try {
        const res = await fetch("/api/v1/users/me", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) return <div>Loading profile...</div>;
  if (!user) return <div>Failed to load profile.</div>;

  return (
    <div>
      <h1>User Profile</h1>
      <div style={{ background: "white", padding: "20px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", maxWidth: "600px" }}>
        <p><strong>ID:</strong> {user.id}</p>
        <p><strong>Name:</strong> {user.name}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>NIN:</strong> {user.nin || "Not Provided"}</p>
        <p><strong>Date of Birth:</strong> {user.dob}</p>
        <p><strong>Nationality:</strong> {user.nationality}</p>
        <p><strong>Gender:</strong> {user.gender}</p>
        <p><strong>State:</strong> {user.state}</p>
        <p><strong>Address:</strong> {user.address}</p>
        <p><strong>Phone Number:</strong> {user.phone_number}</p>
        <p><strong>Account Active:</strong> {user.is_active ? "Yes" : "No"}</p>
        <p><strong>Email Verified:</strong> {user.is_email_verified ? "Yes" : "No"}</p>
        <p><strong>Member Since:</strong> {new Date(user.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
