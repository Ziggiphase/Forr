with open('frontend/src/app/dashboard/layout.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

state_additions = '''  const [loading, setLoading] = useState(true);
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
          fetch("/api/v1/users/me", { headers: { Authorization: Bearer  } }),
          fetch("/api/v1/notifications", { headers: { Authorization: Bearer  } })
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
          const res = await fetch(/api/v1/search?q=, {
            headers: { Authorization: Bearer  }
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
  }, [searchQuery]);'''

# Replace useEffect and state
import re
content = re.sub(r'const \[loading, setLoading\] = useState\(true\);.*?fetchUser\(\);\n  }, \[router\]\]\);', state_additions.replace('\\', '\\\\'), content, flags=re.DOTALL)

# Update nav link
old_nav = '<Link href="/dashboard/notifications" style={{ textDecoration: "none", color: "#333" }}>?? Notifications</Link>'
new_nav = '''          <Link href="/dashboard/notifications" style={{ textDecoration: "none", color: "#333", display: "flex", justifyContent: "space-between" }}>
            <span>?? Notifications</span>
            {unreadCount > 0 && <span style={{ background: "red", color: "white", borderRadius: "10px", padding: "2px 8px", fontSize: "12px" }}>{unreadCount}</span>}
          </Link>'''
content = content.replace(old_nav, new_nav)

# Update search bar
old_search = '<input type="search" placeholder="Search..." style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }} />'
new_search = '''            <div style={{ position: "relative" }}>
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
                            <Link key={b.id} href={/dashboard/businesses/} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{b.name} <small style={{ color: "gray" }}>({b.type})</small></Link>
                          ))}
                        </div>
                      )}
                      {searchResults.products?.length > 0 && (
                        <div style={{ padding: "10px", borderTop: "1px solid #eee" }}>
                          <h4 style={{ margin: "0 0 5px 0", fontSize: "12px", color: "gray", textTransform: "uppercase" }}>Products</h4>
                          {searchResults.products.map((p: any) => (
                            <Link key={p.id} href={/dashboard/businesses/} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{p.name} <small style={{ color: "gray" }}>in {p.business_name}</small></Link>
                          ))}
                        </div>
                      )}
                      {searchResults.conversations?.length > 0 && (
                        <div style={{ padding: "10px", borderTop: "1px solid #eee" }}>
                          <h4 style={{ margin: "0 0 5px 0", fontSize: "12px", color: "gray", textTransform: "uppercase" }}>Conversations</h4>
                          {searchResults.conversations.map((c: any) => (
                            <Link key={c.id} href={/dashboard/businesses//inbox?conversation=} style={{ display: "block", textDecoration: "none", color: "black", padding: "5px 0" }}>{c.customer_name || c.customer_identifier} <small style={{ color: "gray" }}>in {c.business_name}</small></Link>
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
            </div>'''
content = content.replace(old_search, new_search)

with open('frontend/src/app/dashboard/layout.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
