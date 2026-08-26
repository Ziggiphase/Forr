"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("Verifying your email...");

  useEffect(() => {
    if (!token) {
      setStatus("Invalid or missing token.");
      return;
    }

    const verify = async () => {
      try {
        const res = await fetch(`/api/v1/auth/verify-email?token=${token}`);
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Verification failed");
        }
        setStatus("Email verified successfully! You can now log in.");
        setTimeout(() => router.push("/login"), 3000);
      } catch (err: any) {
        setStatus(err.message);
      }
    };

    verify();
  }, [token, router]);

  return (
    <div style={{ maxWidth: "400px", margin: "60px auto", textAlign: "center", fontFamily: "sans-serif" }}>
      <h2>Email Verification</h2>
      <p>{status}</p>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
