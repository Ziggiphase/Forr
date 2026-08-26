with open('frontend/src/app/dashboard/businesses/[id]/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Payments tab button
tab_btn = '''        <button 
          onClick={() => setActiveTab("payments")} 
          style={{ 
            background: activeTab === "payments" ? "black" : "#f4f4f4", 
            color: activeTab === "payments" ? "white" : "black",
            border: "1px solid black", 
            borderBottom: "none",
            padding: "10px 20px",
            borderTopLeftRadius: "8px",
            borderTopRightRadius: "8px",
            cursor: "pointer", 
            fontSize: "16px", 
            fontWeight: "bold" 
          }}>
          Payments
        </button>
        <Link href={/dashboard/businesses//inbox}'''

content = content.replace('        <Link href={/dashboard/businesses//inbox}', tab_btn)

# We also need state for banks and payments form
state_hooks = '''  const [agentTone, setAgentTone] = useState("");
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
        headers: { Authorization: Bearer  }
      })
      .then(res => res.json())
      .then(data => setBanks(data))
      .catch(err => console.error(err));
    }
  }, [activeTab]);

  const verifyAccount = async () => {
    setPaymentsLoading(true);
    try {
      // In a real app we might have a dedicated verify endpoint, but we can just require the user to type exactly, or we can use Paystack resolve.
      // Wait, the backend subaccount creation verifies it. We can just submit.
      alert("Verification happens during save!");
    } finally {
      setPaymentsLoading(false);
    }
  };

  const savePaymentsConfig = async () => {
    setPaymentsLoading(true);
    try {
      const bankName = banks.find(b => b.code === bankCode)?.name || "";
      const res = await fetch(/api/v1/businesses//subaccount, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: Bearer 
        },
        body: JSON.stringify({
          bank_code: bankCode,
          account_number: accountNumber,
          account_name: accountName,
          bank_name: bankName
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert("Payments configured successfully!");
        fetchData();
      } else {
        alert(data.detail || "Error configuring payments");
      }
    } catch(err) {
      alert("Network error");
    } finally {
      setPaymentsLoading(false);
    }
  };
'''

content = content.replace('  const [agentTone, setAgentTone] = useState("");\n  const [agentConfigLoading, setAgentConfigLoading] = useState(false);', state_hooks)


payments_content = '''        {activeTab === "payments" && (
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

        {activeTab === "settings" && ('''

content = content.replace('        {activeTab === "settings" && (', payments_content)

with open('frontend/src/app/dashboard/businesses/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
