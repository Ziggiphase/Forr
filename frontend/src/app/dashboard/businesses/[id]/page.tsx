"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Cookies from "js-cookie";

const CATEGORIES = [
  "Electronics",
  "Clothing & Apparel",
  "Food & Groceries",
  "Health & Beauty",
  "Home & Furniture",
  "Services",
  "Other"
];

const REQUIRED_FIELDS = [
  { key: "name", label: "Product Name" },
  { key: "price", label: "Price (₦)" },
  { key: "description", label: "Description (Optional)" },
  { key: "quantity", label: "Stock/Quantity" },
  { key: "category", label: "Category" }
];

export default function BusinessDashboardPage() {
  const params = useParams();
  const { id } = params as { id: string };

  const [business, setBusiness] = useState<any>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("catalogue");

  // Integration state
  const [telegramToken, setTelegramToken] = useState("");
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [whatsappSid, setWhatsappSid] = useState("");
  const [whatsappToken, setWhatsappToken] = useState("");
  const [whatsappLoading, setWhatsappLoading] = useState(false);

  // AI Agent Config state
  const [agentKnowledge, setAgentKnowledge] = useState<any>({
    delivery_fee: "",
    return_policy: "",
    business_hours: ""
  });
  const [agentTone, setAgentTone] = useState("");
  const [agentConfigLoading, setAgentConfigLoading] = useState(false);

  // Payments State
  const [banks, setBanks] = useState<any[]>([]);
  const [bankCode, setBankCode] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [accountName, setAccountName] = useState("");
  const [paymentsLoading, setPaymentsLoading] = useState(false);
  
  useEffect(() => {
    if (activeTab === "payments" && banks.length === 0) {
      fetch("/api/v1/businesses/banks", {
        headers: { Authorization: "Bearer " + Cookies.get("access_token") }
      })
      .then(res => res.json())
      .then(data => setBanks(data))
      .catch(err => console.error(err));
    }
  }, [activeTab]);

  const verifyAccount = async () => {
    setPaymentsLoading(true);
    try {
      alert("Verification happens during save!");
    } finally {
      setPaymentsLoading(false);
    }
  };

  const savePaymentsConfig = async () => {
    setPaymentsLoading(true);
    try {
      const bName = banks.find(b => b.code === bankCode)?.name || "";
      const res = await fetch(`/api/v1/businesses/${id}/subaccount`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + Cookies.get("access_token")
        },
        body: JSON.stringify({
          bank_code: bankCode,
          account_number: accountNumber,
          account_name: accountName,
          bank_name: bName
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert("Payments configured successfully!");
        window.location.reload();
      } else {
        alert(data.detail || "Error configuring payments");
      }
    } catch(err) {
      alert("Network error");
    } finally {
      setPaymentsLoading(false);
    }
  };


  // Single editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<any>({});
  
  // Single adding state
  const [isAdding, setIsAdding] = useState(false);
  const [newForm, setNewForm] = useState<any>({
    name: "", price: 0, description: "", quantity: 0, category: CATEGORIES[0], status: "draft"
  });

  // Bulk Upload State
  const [uploadStep, setUploadStep] = useState(0); // 0 = closed, 1 = upload, 2 = mapping
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadHeaders, setUploadHeaders] = useState<string[]>([]);
  const [uploadData, setUploadData] = useState<any[]>([]);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [columnMap, setColumnMap] = useState<Record<string, string>>({});

  const fetchBusinessAndProducts = async () => {
    const token = Cookies.get("access_token");
    try {
      const [bizRes, prodRes] = await Promise.all([
        fetch(`/api/v1/businesses/${id}`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`/api/v1/businesses/${id}/products`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      if (!bizRes.ok) throw new Error("Failed to fetch business");
      const bizData = await bizRes.json();
      setBusiness(bizData);
      if (bizData.agent_knowledge) setAgentKnowledge(bizData.agent_knowledge);
      if (bizData.agent_tone) setAgentTone(bizData.agent_tone);
      
      if (prodRes.ok) setProducts(await prodRes.json());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBusinessAndProducts();
  }, [id]);

  const handleSaveAgentConfig = async () => {
    setAgentConfigLoading(true);
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/agent-config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          agent_knowledge: agentKnowledge,
          agent_tone: agentTone
        })
      });
      if (!res.ok) throw new Error("Failed to save config");
      alert("AI Agent Config saved!");
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setAgentConfigLoading(false);
    }
  };

  const handleAddSubmit = async () => {
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(newForm)
      });
      if (!res.ok) throw new Error("Failed to add product");
      
      setIsAdding(false);
      setNewForm({ name: "", price: 0, description: "", quantity: 0, category: CATEGORIES[0], status: "draft" });
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleEditClick = (product: any) => {
    setEditingId(product.id);
    setEditForm({ ...product });
  };

  const handleEditSave = async () => {
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/products/${editingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(editForm)
      });
      if (!res.ok) throw new Error("Failed to update product");
      
      setEditingId(null);
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (productId: string) => {
    if (!confirm("Are you sure you want to delete this product?")) return;
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/products/${productId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to delete product");
      
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Upload Handlers
  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploadLoading(true);

    const token = Cookies.get("access_token");
    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await fetch(`/api/v1/businesses/${id}/products/upload/parse`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Upload failed");
      }
      
      const data = await res.json();
      setUploadHeaders(data.headers);
      setUploadData(data.data);
      
      const autoMap: Record<string, string> = {};
      REQUIRED_FIELDS.forEach(field => {
        const match = data.headers.find((h: string) => h.toLowerCase() === field.key.toLowerCase());
        if (match) {
          autoMap[field.key] = match;
        }
      });
      setColumnMap(autoMap);
      
      setUploadStep(2);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleBulkImport = async () => {
    // Requires Name and Price to be mapped
    if (!columnMap.name || !columnMap.price) {
      alert("Please map at least Product Name and Price.");
      return;
    }

    setUploadLoading(true);

    // Transform raw data
    const payload = uploadData.map(row => {
      const p = parseFloat(row[columnMap.price]);
      const q = parseInt(row[columnMap.quantity], 10);
      
      let cat = "Other";
      if (columnMap.category && row[columnMap.category]) {
        const val = row[columnMap.category].toString().trim();
        // Exact match or fallback to Other
        if (CATEGORIES.includes(val)) {
          cat = val;
        } else if (CATEGORIES.some(c => c.toLowerCase() === val.toLowerCase())) {
           cat = CATEGORIES.find(c => c.toLowerCase() === val.toLowerCase()) || "Other";
        }
      }

      return {
        name: String(row[columnMap.name] || "Untitled Product"),
        price: isNaN(p) ? 0 : p,
        description: columnMap.description ? String(row[columnMap.description] || "") : "",
        quantity: isNaN(q) ? 0 : q,
        category: cat,
        status: "draft"
      };
    });

    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/products/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Bulk import failed");
      
      setUploadStep(0);
      setUploadFile(null);
      setColumnMap({});
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleConnectTelegram = async () => {
    if (!telegramToken) return;
    setTelegramLoading(true);
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/integrations/telegram`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ token: telegramToken })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Failed to connect");
      }
      setTelegramToken("");
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleConnectWhatsapp = async () => {
    if (!whatsappSid || !whatsappToken) return;
    setWhatsappLoading(true);
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/integrations/whatsapp`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ twilio_sid: whatsappSid, twilio_auth_token: whatsappToken })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Failed to connect");
      }
      setWhatsappSid("");
      setWhatsappToken("");
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setWhatsappLoading(false);
    }
  };

  const handleDisconnectWhatsapp = async () => {
    setWhatsappLoading(true);
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/integrations/whatsapp`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to disconnect");
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setWhatsappLoading(false);
    }
  };

  const handleDisconnectTelegram = async () => {
    if (!confirm("Disconnect Telegram?")) return;
    setTelegramLoading(true);
    const token = Cookies.get("access_token");
    try {
      const res = await fetch(`/api/v1/businesses/${id}/integrations/telegram`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to disconnect");
      fetchBusinessAndProducts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setTelegramLoading(false);
    }
  };


  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!business) return <div>No business data</div>;

  const thStyle = { padding: "10px", borderBottom: "2px solid #ddd", textAlign: "left" as const, background: "#f9f9f9" };
  const tdStyle = { padding: "10px", borderBottom: "1px solid #ddd" };
  const inputStyle = { width: "100%", padding: "5px", boxSizing: "border-box" as const };

  return (
    <div style={{ fontFamily: "sans-serif" }}>
      <Link href="/dashboard" style={{ textDecoration: "none", color: "blue", marginBottom: "20px", display: "inline-block" }}>
        &larr; Back to all businesses
      </Link>
      
      <div style={{ background: "white", padding: "30px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", marginBottom: "30px" }}>
        <h1 style={{ marginTop: 0 }}>{business.name}</h1>
        <p style={{ color: "gray", fontSize: "14px", marginTop: "-10px" }}>{business.business_type} • {business.service_mode}</p>
      </div>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "2px solid black", paddingBottom: "0" }}>
        <button 
          onClick={() => setActiveTab("catalogue")} 
          style={{ 
            background: activeTab === "catalogue" ? "black" : "#f4f4f4", 
            color: activeTab === "catalogue" ? "white" : "black",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold" 
          }}>
          Manage Products
        </button>
        <button 
          onClick={() => setActiveTab("settings")} 
          style={{ 
            background: activeTab === "settings" ? "black" : "#f4f4f4", 
            color: activeTab === "settings" ? "white" : "black",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold" 
          }}>
          Business Integrations & Settings
        </button>
        <button 
          onClick={() => setActiveTab("agent")} 
          style={{ 
            background: activeTab === "agent" ? "black" : "#f4f4f4", 
            color: activeTab === "agent" ? "white" : "black",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold" 
          }}>
          AI Agent Knowledge
        </button>
        <Link href={`/dashboard/businesses/${id}/inbox`} style={{
            background: "#f4f4f4", 
            color: "blue",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold",
            textDecoration: "none"
        }}>
          Go to Inbox &rarr;
        </Link>
        <Link href={`/dashboard/businesses/${id}/analytics`} style={{
            background: "#f4f4f4", 
            color: "green",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold",
            textDecoration: "none"
        }}>
          Analytics Dashboard &rarr;
        </Link>
      </div>

      <div style={{ background: "white", padding: "30px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", position: "relative" }}>
        
        {/* Modals for Uploading */}
        {uploadStep > 0 && (
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(255,255,255,0.95)", zIndex: 10, padding: "30px", borderRadius: "8px" }}>
            <div style={{ maxWidth: "500px", margin: "0 auto", background: "white", border: "1px solid #ccc", padding: "20px", borderRadius: "8px", boxShadow: "0 4px 10px rgba(0,0,0,0.1)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
                <h2 style={{ margin: 0 }}>{uploadStep === 1 ? "Upload Catalogue" : "Map Columns"}</h2>
                <button onClick={() => { setUploadStep(0); setUploadFile(null); }} style={{ background: "transparent", border: "none", fontSize: "20px", cursor: "pointer" }}>&times;</button>
              </div>

              {uploadStep === 1 && (
                <form onSubmit={handleFileUpload}>
                  <p>Upload your CSV, Excel, PDF, or DOCX file containing your products.</p>
                  <input type="file" accept=".csv, .xlsx, .xls, .pdf, .docx" onChange={e => setUploadFile(e.target.files?.[0] || null)} required style={{ marginBottom: "20px" }} />
                  <br />
                  <button disabled={uploadLoading} type="submit" style={{ padding: "10px 20px", background: "blue", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                    {uploadLoading ? "Parsing..." : "Next: Map Columns"}
                  </button>
                </form>
              )}

              {uploadStep === 2 && (
                <div>
                  <p>We found {uploadData.length} rows. Match your file's columns to the required fields below:</p>
                  
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "20px" }}>
                    {REQUIRED_FIELDS.map(field => (
                      <div key={field.key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <label style={{ fontWeight: "bold" }}>{field.label} {["name", "price"].includes(field.key) && <span style={{color: "red"}}>*</span>}</label>
                        <select 
                          value={columnMap[field.key] || ""} 
                          onChange={(e) => setColumnMap({...columnMap, [field.key]: e.target.value})}
                          style={{ padding: "5px", width: "200px" }}
                        >
                          <option value="">-- Ignore / Default --</option>
                          {uploadHeaders.map(h => <option key={h} value={h}>{h}</option>)}
                        </select>
                      </div>
                    ))}
                  </div>

                  <button disabled={uploadLoading} onClick={handleBulkImport} style={{ padding: "10px 20px", background: "green", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", width: "100%" }}>
                    {uploadLoading ? "Importing..." : `Import ${uploadData.length} Products as Drafts`}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "catalogue" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ margin: 0 }}>Product Catalogue</h2>
              <div style={{ display: "flex", gap: "10px" }}>
                <button 
                  onClick={() => setUploadStep(1)}
                  style={{ padding: "8px 16px", background: "white", color: "blue", border: "1px solid blue", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
                >
                  ⬆ Bulk Upload
                </button>
                <button 
                  onClick={() => setIsAdding(!isAdding)}
                  style={{ padding: "8px 16px", background: "blue", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
                >
                  {isAdding ? "Cancel" : "+ Add Product"}
                </button>
              </div>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
                <thead>
                  <tr>
                    <th style={thStyle}>Name</th>
                    <th style={thStyle}>Category</th>
                    <th style={thStyle}>Price (₦)</th>
                    <th style={thStyle}>Stock</th>
                    <th style={thStyle}>Status</th>
                    <th style={thStyle}>Description</th>
                    <th style={thStyle}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {isAdding && (
                    <tr style={{ background: "#f0f8ff" }}>
                      <td style={tdStyle}><input style={inputStyle} value={newForm.name} onChange={e => setNewForm({...newForm, name: e.target.value})} placeholder="Name" /></td>
                      <td style={tdStyle}>
                        <select style={inputStyle} value={newForm.category} onChange={e => setNewForm({...newForm, category: e.target.value})}>
                          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </td>
                      <td style={tdStyle}><input type="number" style={inputStyle} value={newForm.price} onChange={e => setNewForm({...newForm, price: parseFloat(e.target.value)})} /></td>
                      <td style={tdStyle}><input type="number" style={inputStyle} value={newForm.quantity} onChange={e => setNewForm({...newForm, quantity: parseInt(e.target.value, 10)})} /></td>
                      <td style={tdStyle}>
                        <select style={inputStyle} value={newForm.status} onChange={e => setNewForm({...newForm, status: e.target.value})}>
                          <option value="draft">Draft</option>
                          <option value="active">Active</option>
                        </select>
                      </td>
                      <td style={tdStyle}><input style={inputStyle} value={newForm.description} onChange={e => setNewForm({...newForm, description: e.target.value})} placeholder="Description" /></td>
                      <td style={tdStyle}>
                        <button onClick={handleAddSubmit} style={{ background: "green", color: "white", border: "none", padding: "5px 10px", borderRadius: "4px", cursor: "pointer" }}>Save</button>
                      </td>
                    </tr>
                  )}

                  {products.length === 0 && !isAdding && (
                    <tr>
                      <td colSpan={7} style={{ padding: "30px", textAlign: "center", color: "gray" }}>
                        No products added yet. Click "+ Add Product" or "Bulk Upload" to get started.
                      </td>
                    </tr>
                  )}

                  {products.map(prod => (
                    <tr key={prod.id} style={{ background: editingId === prod.id ? "#fffde7" : (prod.status === "draft" ? "#fdfbf7" : "transparent") }}>
                      {editingId === prod.id ? (
                        <>
                          <td style={tdStyle}><input style={inputStyle} value={editForm.name} onChange={e => setEditForm({...editForm, name: e.target.value})} /></td>
                          <td style={tdStyle}>
                            <select style={inputStyle} value={editForm.category} onChange={e => setEditForm({...editForm, category: e.target.value})}>
                              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                          </td>
                          <td style={tdStyle}><input type="number" style={inputStyle} value={editForm.price} onChange={e => setEditForm({...editForm, price: parseFloat(e.target.value)})} /></td>
                          <td style={tdStyle}><input type="number" style={inputStyle} value={editForm.quantity} onChange={e => setEditForm({...editForm, quantity: parseInt(e.target.value, 10)})} /></td>
                          <td style={tdStyle}>
                            <select style={inputStyle} value={editForm.status} onChange={e => setEditForm({...editForm, status: e.target.value})}>
                              <option value="draft">Draft</option>
                              <option value="active">Active</option>
                            </select>
                          </td>
                          <td style={tdStyle}><input style={inputStyle} value={editForm.description || ""} onChange={e => setEditForm({...editForm, description: e.target.value})} /></td>
                          <td style={{ ...tdStyle, display: "flex", gap: "5px" }}>
                            <button onClick={handleEditSave} style={{ background: "green", color: "white", border: "none", padding: "5px", borderRadius: "4px", cursor: "pointer" }}>Save</button>
                            <button onClick={() => setEditingId(null)} style={{ background: "gray", color: "white", border: "none", padding: "5px", borderRadius: "4px", cursor: "pointer" }}>Cancel</button>
                          </td>
                        </>
                      ) : (
                        <>
                          <td style={tdStyle}><strong>{prod.name}</strong></td>
                          <td style={tdStyle}>
                            <span style={{ background: "#eee", padding: "2px 6px", borderRadius: "4px", fontSize: "12px" }}>{prod.category}</span>
                          </td>
                          <td style={tdStyle}>{prod.price}</td>
                          <td style={tdStyle}>{prod.quantity}</td>
                          <td style={tdStyle}>
                            <span style={{ color: prod.status === "active" ? "green" : "goldenrod", fontWeight: "bold", textTransform: "capitalize" }}>
                              {prod.status}
                            </span>
                          </td>
                          <td style={tdStyle}><span style={{ color: "gray", fontSize: "13px" }}>{prod.description || "-"}</span></td>
                          <td style={tdStyle}>
                            <button onClick={() => handleEditClick(prod)} style={{ background: "transparent", border: "1px solid #ccc", padding: "4px 8px", borderRadius: "4px", cursor: "pointer", marginRight: "5px" }}>Edit</button>
                            <button onClick={() => handleDelete(prod.id)} style={{ background: "transparent", border: "1px solid red", color: "red", padding: "4px 8px", borderRadius: "4px", cursor: "pointer" }}>Delete</button>
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "payments" && (
          <div>
            <h2 style={{ margin: 0, marginBottom: "20px" }}>Payments (Paystack)</h2>
            <p style={{ color: "gray", fontSize: "14px", marginBottom: "30px" }}>
              Enable your AI agent to generate payment links and process sales automatically. 
              Funds are settled to your bank account securely by Paystack on a standard T+1 / T+2 schedule.
            </p>

            <div style={{ maxWidth: "500px", border: "1px solid #ddd", padding: "20px", borderRadius: "8px" }}>
              {business.paystack_subaccount_code ? (
                <div>
                  <p style={{ color: "green", fontWeight: "bold" }}>? Payments Enabled</p>
                  <p>Bank: {business.bank_name}</p>
                  <p>Account: {business.bank_account_number}</p>
                  <p>Name: {business.bank_account_name}</p>
                  <p style={{ color: "gray", fontSize: "12px", marginTop: "10px" }}>Your AI agent will now generate payment links for customers when they are ready to buy.</p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
                  <div>
                    <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Select Bank</label>
                    <select 
                      value={bankCode} 
                      onChange={e => setBankCode(e.target.value)}
                      style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
                    >
                      <option value="">-- Choose a Bank --</option>
                      {banks.map(b => (
                        <option key={b.code} value={b.code}>{b.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Account Number</label>
                    <input 
                      type="text" 
                      value={accountNumber} 
                      onChange={e => setAccountNumber(e.target.value)}
                      style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
                    />
                  </div>
                  <div>
                    <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Account Name (Exact Match)</label>
                    <input 
                      type="text" 
                      value={accountName} 
                      onChange={e => setAccountName(e.target.value)}
                      style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
                      placeholder="E.g., John Doe"
                    />
                    <small style={{ color: "gray" }}>This must match your bank account name exactly.</small>
                  </div>
                  <button 
                    disabled={paymentsLoading || !bankCode || !accountNumber || !accountName}
                    onClick={savePaymentsConfig}
                    style={{ background: "black", color: "white", padding: "10px", borderRadius: "4px", border: "none", cursor: "pointer", fontWeight: "bold", marginTop: "10px" }}
                  >
                    {paymentsLoading ? "Verifying & Saving..." : "Enable Payments"}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "settings" && (
          <div>
            <h2 style={{ margin: 0, marginBottom: "20px" }}>Integrations</h2>
            <div style={{ border: "1px solid #ddd", padding: "20px", borderRadius: "8px", maxWidth: "400px" }}>
              <h3 style={{ marginTop: 0 }}>Telegram Bot</h3>
              {business.is_telegram_connected ? (
                <div>
                  <p style={{ color: "green", fontWeight: "bold" }}>✅ Connected</p>
                  <p style={{ color: "gray", fontSize: "14px" }}>We are actively polling your Telegram bot for messages.</p>
                  <button onClick={handleDisconnectTelegram} disabled={telegramLoading} style={{ background: "red", color: "white", padding: "8px 16px", border: "none", borderRadius: "4px", cursor: "pointer", marginTop: "10px" }}>
                     {telegramLoading ? "Disconnecting..." : "Disconnect Bot"}
                  </button>
                </div>
              ) : (
                <div>
                  <p style={{ color: "gray", fontSize: "14px" }}>Connect your Telegram bot (from @BotFather) to receive orders and messages directly.</p>
                  <input 
                    type="text" 
                    placeholder="e.g. 123456789:ABCdefGHIjkl..." 
                    value={telegramToken}
                    onChange={e => setTelegramToken(e.target.value)}
                    style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
                  />
                  <button onClick={handleConnectTelegram} disabled={telegramLoading || !telegramToken} style={{ background: "blue", color: "white", padding: "10px 16px", border: "none", borderRadius: "4px", cursor: "pointer", width: "100%", fontWeight: "bold" }}>
                    {telegramLoading ? "Connecting & Verifying..." : "Connect Telegram"}
                  </button>
                </div>
              )}
            </div>

            <div style={{ border: "1px solid #ddd", padding: "20px", borderRadius: "8px", maxWidth: "400px", marginTop: "20px" }}>
              <h3 style={{ marginTop: 0 }}>WhatsApp (Twilio Sandbox)</h3>
              {business.is_whatsapp_connected ? (
                <div>
                  <p style={{ color: "green", fontWeight: "bold" }}>✅ Connected</p>
                  <p style={{ color: "gray", fontSize: "14px", marginBottom: "5px" }}>Webhook URL configured. Copy this URL into your Twilio Sandbox Settings under "When a message comes in":</p>
                  <div style={{ background: "#f0f0f0", padding: "10px", borderRadius: "4px", fontSize: "12px", wordBreak: "break-all", marginBottom: "15px" }}>
                    <strong>https://jump-sardine-kinship.ngrok-free.dev/api/v1/webhooks/twilio/whatsapp/{id}</strong>
                  </div>
                  <button onClick={handleDisconnectWhatsapp} disabled={whatsappLoading} style={{ background: "red", color: "white", padding: "8px 16px", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                     {whatsappLoading ? "Disconnecting..." : "Disconnect WhatsApp"}
                  </button>
                </div>
              ) : (
                <div>
                  <p style={{ color: "gray", fontSize: "14px" }}>Connect your Twilio Sandbox account to receive WhatsApp messages.</p>
                  <input 
                    type="text" 
                    placeholder="Twilio Account SID" 
                    value={whatsappSid}
                    onChange={e => setWhatsappSid(e.target.value)}
                    style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
                  />
                  <input 
                    type="password" 
                    placeholder="Twilio Auth Token" 
                    value={whatsappToken}
                    onChange={e => setWhatsappToken(e.target.value)}
                    style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
                  />
                  <button onClick={handleConnectWhatsapp} disabled={whatsappLoading || !whatsappSid || !whatsappToken} style={{ background: "green", color: "white", padding: "10px 16px", border: "none", borderRadius: "4px", cursor: "pointer", width: "100%", fontWeight: "bold" }}>
                    {whatsappLoading ? "Connecting..." : "Connect WhatsApp"}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "agent" && (
          <div>
            <h2 style={{ margin: 0, marginBottom: "20px" }}>AI Agent Knowledge Base & Tone</h2>
            <p style={{ color: "gray", fontSize: "14px", marginBottom: "30px" }}>
              Configure the business facts and conversational tone that the AI will use when replying to customers on your behalf.
            </p>

            <div style={{ maxWidth: "600px", display: "flex", flexDirection: "column", gap: "20px" }}>
              
              <div style={{ border: "1px solid #ddd", padding: "20px", borderRadius: "8px" }}>
                <h3 style={{ marginTop: 0 }}>Business Facts</h3>
                <p style={{ fontSize: "14px", color: "gray" }}>Fill in the facts customers ask about most.</p>
                
                <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Delivery Fee / Policy</label>
                <input 
                  type="text"
                  value={agentKnowledge.delivery_fee || ""}
                  onChange={e => setAgentKnowledge({...agentKnowledge, delivery_fee: e.target.value})}
                  placeholder="e.g. ₦1,500 within Lagos, outside Lagos varies."
                  style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
                />

                <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Return Policy</label>
                <input 
                  type="text"
                  value={agentKnowledge.return_policy || ""}
                  onChange={e => setAgentKnowledge({...agentKnowledge, return_policy: e.target.value})}
                  placeholder="e.g. 7-day return policy for unused items."
                  style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
                />

                <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>Business Hours</label>
                <input 
                  type="text"
                  value={agentKnowledge.business_hours || ""}
                  onChange={e => setAgentKnowledge({...agentKnowledge, business_hours: e.target.value})}
                  placeholder="e.g. Monday - Friday, 9AM to 5PM."
                  style={{ width: "100%", padding: "10px", boxSizing: "border-box", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
                />
              </div>

              <div style={{ border: "1px solid #ddd", padding: "20px", borderRadius: "8px" }}>
                <h3 style={{ marginTop: 0 }}>General Chat Tone</h3>
                <p style={{ fontSize: "14px", color: "gray" }}>How should the AI sound? Be as specific as you want.</p>
                <textarea 
                  value={agentTone || ""}
                  onChange={e => setAgentTone(e.target.value)}
                  placeholder="e.g. Be very friendly, use lots of emojis, and always call the customer 'Chief'."
                  style={{ width: "100%", padding: "10px", boxSizing: "border-box", height: "100px", borderRadius: "4px", border: "1px solid #ccc", fontFamily: "inherit" }}
                />
              </div>

              <button 
                onClick={handleSaveAgentConfig} 
                disabled={agentConfigLoading} 
                style={{ background: "black", color: "white", padding: "15px", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", fontSize: "16px" }}
              >
                {agentConfigLoading ? "Saving..." : "Save AI Configuration"}
              </button>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}
