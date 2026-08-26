"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    const token = Cookies.get("access_token");
    try {
      const res = await fetch("/api/v1/notifications", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id: string) => {
    const token = Cookies.get("access_token");
    try {
      await fetch(`/api/v1/notifications/${id}/read`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const markAllAsRead = async () => {
    const token = Cookies.get("access_token");
    try {
      await fetch("/api/v1/notifications/read-all", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading notifications...</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1 style={{ margin: 0 }}>Notifications</h1>
        {notifications.some(n => !n.is_read) && (
          <button onClick={markAllAsRead} style={{ background: "black", color: "white", padding: "8px 16px", borderRadius: "4px", border: "none", cursor: "pointer" }}>
            Mark All as Read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <p style={{ color: "gray" }}>You have no notifications.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxWidth: "800px" }}>
          {notifications.map(n => (
            <div key={n.id} style={{ 
              padding: "15px", 
              border: "1px solid #ddd", 
              borderRadius: "8px", 
              background: n.is_read ? "#fff" : "#f0f8ff",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start"
            }}>
              <div>
                <h3 style={{ margin: "0 0 5px 0" }}>{n.title}</h3>
                <p style={{ margin: 0, color: "#333", fontSize: "14px" }}>{n.message}</p>
                <small style={{ color: "gray", display: "block", marginTop: "5px" }}>{new Date(n.created_at).toLocaleString()}</small>
              </div>
              {!n.is_read && (
                <button onClick={() => markAsRead(n.id)} style={{ background: "transparent", color: "blue", border: "none", cursor: "pointer", fontSize: "12px", textDecoration: "underline" }}>
                  Mark Read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
