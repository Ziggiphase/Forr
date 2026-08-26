"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import Cookies from "js-cookie";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any>({ businesses: [], products: [], conversations: [] });
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchUserAndNotifications = async () => {
      try {
        const [userRes, notifRes] = await Promise.all([
          fetch("/api/v1/users/me", { headers: { Authorization: `Bearer ${token}` } }),
          fetch("/api/v1/notifications", { headers: { Authorization: `Bearer ${token}` } })
        ]);
        if (!userRes.ok) throw new Error("Failed to fetch user");
        const userData = await userRes.json();
        setUser(userData);
        
        if (notifRes.ok) {
          const notifData = await notifRes.json();
          setUnreadCount(notifData.filter((n: any) => !n.is_read).length);
        }
      } catch (err) {
        Cookies.remove("access_token");
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserAndNotifications();
  }, [router, pathname]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        setIsSearching(true);
        const token = Cookies.get("access_token");
        try {
          const res = await fetch(`/api/v1/search?q=${searchQuery}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const data = await res.json();
          setSearchResults(data);
          setShowSearchDropdown(true);
        } catch (e) {
          console.error(e);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults({ businesses: [], products: [], conversations: [] });
        setShowSearchDropdown(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const handleLogout = () => {
    Cookies.remove("access_token");
    router.push("/login");
  };

  if (loading) {
    return <div>Loading Dashboard...</div>;
  }

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw", fontFamily: "sans-serif" }}>
      {/* Sidebar */}
      <aside style={{ width: "250px", background: "#f4f4f4", padding: "20px", display: "flex", flexDirection: "column" }}>
        <h2>Forr</h2>
        <nav style={{ display: "flex", flexDirection: "column", gap: "15px", marginTop: "30px", flexGrow: 1 }}>
          <Link href="/dashboard" style={{ textDecoration: "none", color: "#333" }}>🏢 Businesses</Link>
          <Link href="/dashboard/profile" style={{ textDecoration: "none", color: "#333" }}>👤 Profile</Link>
          <Link href="/dashboard/billing" style={{ textDecoration: "none", color: "#333" }}>💳 Billing</Link>
          <Link href="/dashboard/faqs" style={{ textDecoration: "none", color: "#333" }}>❓ FAQs</Link>
          <Link href="/dashboard/settings" style={{ textDecoration: "none", color: "#333" }}>⚙️ Settings</Link>
          <Link href="/dashboard/notifications" style={{ textDecoration: "none", color: "#333" }}>🔔 Notifications</Link>
        </nav>
        <button onClick={handleLogout} style={{ marginTop: "auto", padding: "10px", background: "red", color: "white", border: "none", cursor: "pointer" }}>
          Log Out
        </button>
      </aside>

      {/* Main Content */}
      <div style={{ flexGrow: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
        {/* Header */}
        <header style={{ height: "60px", minHeight: "60px", borderBottom: "1px solid #ccc", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 20px" }}>
          <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
                        <div style={{ position: "relative" }}>
              <input 
                type="search" 
                placeholder="Search businesses, products, chats..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => { if (searchQuery.length >= 2) setShowSearchDropdown(true); }}
                onBlur={() => setTimeout(() => setShowSearchDropdown(false), 200)}
                style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "300px" }} 
              />
              {showSearchDropdown && (
                <div style={{ position: "absolute", top: "40px", left: 0, right: 0, background: "white", border: "1px solid #ccc", borderRadius: "4px", boxShadow: "0 4px 6px rgba(0,0,0,0.1)", zIndex: 50, maxHeight: "400px", overflowY: "auto" }}>
                  {isSearching ? (
                    <div style={{ padding: "10px", color: "gray" }}>Searching...</div>
                  ) : (
                    <>
                      {searchResults.businesses?.length > 0 && (
                        <div style={{ padding: "10px" }}>
                          <h4 style={{ margin: "0 0 5px 0", fontSize: "12px", color: "gray", textTransform: "uppercase" }}>Businesses</h4>
                          {searchResults.businesses.map((b: any) => (
                            <Link key={b.id} href={`/dashboard/businesses/${b.id}`} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{b.name} <small style={{ color: "gray" }}>({b.type})</small></Link>
                          ))}
                        </div>
                      )}
                      {searchResults.products?.length > 0 && (
                        <div style={{ padding: "10px", borderTop: "1px solid #eee" }}>
                          <h4 style={{ margin: "0 0 5px 0", fontSize: "12px", color: "gray", textTransform: "uppercase" }}>Products</h4>
                          {searchResults.products.map((p: any) => (
                            <Link key={p.id} href={`/dashboard/businesses/${p.business_id}`} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{p.name} <small style={{ color: "gray" }}>in {p.business_name}</small></Link>
                          ))}
                        </div>
                      )}
                      {searchResults.conversations?.length > 0 && (
                        <div style={{ padding: "10px", borderTop: "1px solid #eee" }}>
                          <h4 style={{ margin: "0 0 5px 0", fontSize: "12px", color: "gray", textTransform: "uppercase" }}>Conversations</h4>
                          {searchResults.conversations.map((c: any) => (
                            <Link key={c.id} href={`/dashboard/businesses/${c.business_id}/inbox?conversation=${c.id}`} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{c.customer_name || c.customer_identifier} <small style={{ color: "gray" }}>in {c.business_name}</small></Link>
                          ))}
                        </div>
                      )}
                      {!searchResults.businesses?.length && !searchResults.products?.length && !searchResults.conversations?.length && (
                         <div style={{ padding: "10px", color: "gray" }}>No results found.</div>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
          <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
            <span style={{ fontSize: "14px", color: "gray" }}>○ AI Offline</span>
            <span style={{ fontSize: "14px" }}>Tokens Used: <b>{user?.total_tokens_used || 0}</b></span>
            <span style={{ fontWeight: "bold" }}>Welcome, {user?.name}</span>
          </div>
        </header>

        {/* Page Content */}
        <main style={{ 
          flexGrow: 1, 
          display: "flex", 
          flexDirection: "column",
          padding: pathname?.includes('/inbox') ? '0' : '20px',
          overflow: pathname?.includes('/inbox') ? 'hidden' : 'auto'
        }}>
          {children}
        </main>
      </div>
    </div>
  );
}
