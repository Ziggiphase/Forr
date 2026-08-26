"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";

export default function BillingPage() {
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = Cookies.get("access_token");
    if (!token) return;

    try {
      const bizRes = await fetch("/api/v1/businesses", {
        headers: { Authorization: "Bearer " + token }
      });
      const bizData = await bizRes.json();
      
      const bizWithBilling = await Promise.all(bizData.map(async (biz: any) => {
        try {
          const billRes = await fetch("/api/v1/businesses/" + biz.id + "/billing/status", {
            headers: { Authorization: "Bearer " + token }
          });
          if (billRes.ok) {
            const billData = await billRes.json();
            return { ...biz, billing: billData };
          }
        } catch (e) {
          console.error(e);
        }
        return { ...biz, billing: null };
      }));
      
      setBusinesses(bizWithBilling);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (businessId: string, plan: string) => {
    const token = Cookies.get("access_token");
    if (!token) return;

    try {
      const res = await fetch("/api/v1/businesses/" + businessId + "/billing/upgrade", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token
        },
        body: JSON.stringify({ plan })
      });
      const data = await res.json();
      if (res.ok) {
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
        } else {
          alert(data.message || "Plan updated!");
          fetchData();
        }
      } else {
        alert(data.detail || "Error upgrading plan");
      }
    } catch (err) {
      console.error(err);
      alert("Error processing request");
    }
  };

  if (loading) {
    return <div style={{ padding: "40px" }}>Loading billing info...</div>;
  }

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "40px" }}>
      <h1 style={{ fontSize: "28px", marginBottom: "30px", fontWeight: "bold" }}>Billing & Subscriptions</h1>
      
      {businesses.length === 0 ? (
        <p>You have no businesses yet.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
          {businesses.map(biz => (
            <div key={biz.id} style={{ border: "1px solid #e0e0e0", borderRadius: "12px", overflow: "hidden" }}>
              <div style={{ background: "#f8f9fa", padding: "20px", borderBottom: "1px solid #e0e0e0" }}>
                <h2 style={{ margin: 0, fontSize: "20px" }}>{biz.name}</h2>
                <p style={{ margin: "5px 0 0 0", color: "#666" }}>Manage subscription for this business</p>
              </div>
              
              {biz.billing ? (
                <div style={{ padding: "20px" }}>
                  
                  {biz.billing.usage >= biz.billing.limit && (
                    <div style={{ background: "#fee2e2", border: "1px solid #ef4444", color: "#b91c1c", padding: "15px", borderRadius: "8px", marginBottom: "20px" }}>
                      <strong>! AI Agent Paused - Limit Reached!</strong>
                      <p style={{ margin: "5px 0 0 0" }}>You have reached your conversation limit for this billing cycle. Please upgrade your plan to resume AI agent services.</p>
                    </div>
                  )}

                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px", background: "#f0fdf4", padding: "15px", borderRadius: "8px" }}>
                    <div>
                      <div style={{ fontSize: "14px", color: "#666", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "5px" }}>Current Plan</div>
                      <div style={{ fontSize: "24px", fontWeight: "bold", textTransform: "capitalize" }}>{biz.billing.tier} Tier</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "14px", color: "#666", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "5px" }}>Conversations Used</div>
                      <div style={{ fontSize: "24px", fontWeight: "bold" }}>{biz.billing.usage} / {biz.billing.limit}</div>
                    </div>
                  </div>
                  
                  <div style={{ width: "100%", background: "#e0e0e0", height: "8px", borderRadius: "4px", marginBottom: "30px", overflow: "hidden" }}>
                    <div style={{ 
                      width: Math.min(100, (biz.billing.usage / biz.billing.limit) * 100) + "%", 
                      background: biz.billing.usage >= biz.billing.limit ? "#ef4444" : "#3b82f6", 
                      height: "100%" 
                    }}></div>
                  </div>

                  <h3 style={{ fontSize: "18px", marginBottom: "15px" }}>Available Plans</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "15px" }}>
                    {Object.entries(biz.billing.available_tiers).map(([planName, planDetails]: [string, any]) => {
                      const isCurrent = biz.billing.tier === planName;
                      return (
                        <div key={planName} style={{ border: isCurrent ? "2px solid #3b82f6" : "1px solid #ccc", padding: "15px", borderRadius: "8px", textAlign: "center", position: "relative" }}>
                          {isCurrent && <div style={{ position: "absolute", top: "-10px", right: "-10px", background: "#3b82f6", color: "white", padding: "2px 8px", borderRadius: "10px", fontSize: "12px", fontWeight: "bold" }}>Active</div>}
                          <h4 style={{ margin: "0 0 10px 0", textTransform: "capitalize", fontSize: "18px" }}>{planName}</h4>
                          <div style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "5px" }}>NGN {planDetails.price_ngn.toLocaleString()}</div>
                          <div style={{ fontSize: "14px", color: "#666", marginBottom: "20px" }}>{planDetails.limit.toLocaleString()} conv / month</div>
                          
                          <button 
                            disabled={isCurrent}
                            onClick={() => handleUpgrade(biz.id, planName)}
                            style={{ 
                              width: "100%", 
                              padding: "10px", 
                              borderRadius: "4px", 
                              border: "none", 
                              fontWeight: "bold",
                              cursor: isCurrent ? "not-allowed" : "pointer",
                              background: isCurrent ? "#e0e0e0" : "#000",
                              color: isCurrent ? "#888" : "#fff"
                            }}
                          >
                            {isCurrent ? "Current Plan" : (planDetails.price_ngn > (biz.billing.available_tiers[biz.billing.tier]?.price_ngn || 0) ? "Upgrade" : "Downgrade")}
                          </button>
                        </div>
                      );
                    })}
                  </div>

                </div>
              ) : (
                <div style={{ padding: "20px" }}>Could not load billing details.</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
