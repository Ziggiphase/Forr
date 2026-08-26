"use client";

import { useState } from "react";

const FAQItem = ({ question, answer }: { question: string, answer: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ borderBottom: "1px solid #ddd", padding: "15px 0" }}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{ width: "100%", textAlign: "left", background: "none", border: "none", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "16px", fontWeight: "bold", padding: 0 }}
      >
        {question}
        <span style={{ fontSize: "20px" }}>{isOpen ? "-" : "+"}</span>
      </button>
      {isOpen && (
        <div style={{ marginTop: "10px", color: "#555", lineHeight: "1.5" }}>
          {answer}
        </div>
      )}
    </div>
  );
};

export default function FAQsPage() {
  const faqs = [
    {
      question: "What is Forr?",
      answer: "Forr is an AI-powered conversational commerce platform that allows businesses to automate their sales and customer support on channels like WhatsApp and Telegram. Your AI agent can answer questions, showcase products, and generate payment links 24/7."
    },
    {
      question: "How do I connect my WhatsApp or Telegram?",
      answer: "Each business you create has its own dedicated channels. Go to the 'Businesses' tab, click on your business, and open the 'Business Integrations & Settings' tab to find the connection instructions for Twilio WhatsApp and Telegram BotFather."
    },
    {
      question: "How do payouts work?",
      answer: "Forr uses Paystack to process payments. When a customer pays via the AI-generated link, the funds are automatically routed to the bank account you configured in the Payments tab. Funds are settled on a standard T+1 / T+2 schedule by Paystack."
    },
    {
      question: "What happens if I reach my conversation limit?",
      answer: "When your business reaches its monthly conversation limit based on your active billing tier, the AI agent is temporarily paused. Customers will receive a generic fallback message, and you will receive an email and in-app notification. You can resume service by upgrading your plan in the Billing dashboard."
    },
    {
      question: "How do I update my catalogue?",
      answer: "You can manage your products directly in the Business Dashboard under 'Manage Products'. You can add them one by one or bulk import them using a CSV file."
    }
  ];

  return (
    <div>
      <h1 style={{ margin: "0 0 20px 0" }}>Frequently Asked Questions</h1>
      <p style={{ color: "gray", marginBottom: "30px" }}>Find answers to common questions about setting up and using your Forr AI agents.</p>
      
      <div style={{ maxWidth: "800px", background: "white", padding: "20px 30px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        {faqs.map((faq, index) => (
          <FAQItem key={index} question={faq.question} answer={faq.answer} />
        ))}
      </div>
    </div>
  );
}
