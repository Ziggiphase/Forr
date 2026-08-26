'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { format } from 'date-fns';
import Cookies from "js-cookie";

type Conversation = {
  id: string;
  business_id: string;
  channel: string;
  customer_identifier: string;
  customer_name: string | null;
  status: string;
  last_activity_at: string;
  is_unread: boolean;
};

type Message = {
  id: string;
  conversation_id: string;
  sender_type: string;
  content: string;
  created_at: string;
};

import Link from "next/link";

export default function InboxPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Poll intervals
  const CONVERSATION_POLL_MS = 10000; // 10s
  const MESSAGE_POLL_MS = 5000; // 5s

  const fetchConversations = async () => {
    try {
      const token = Cookies.get("access_token");
      const res = await fetch(`/api/v1/businesses/${id}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (err) {
      console.error("Failed to fetch conversations", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMessages = async (conversationId: string) => {
    try {
      const token = Cookies.get("access_token");
      const res = await fetch(`/api/v1/conversations/${conversationId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => {
          const tempMessages = prev.filter(m => m.id.startsWith('temp-') && m.conversation_id === conversationId);
          const newMessages = [...data];
          tempMessages.forEach(tempM => {
            const isDuplicate = data.some((sm: Message) => sm.content === tempM.content && sm.sender_type === tempM.sender_type);
            if (!isDuplicate) {
              newMessages.push(tempM);
            }
          });
          return newMessages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    } catch (err) {
      console.error("Failed to fetch messages", err);
    }
  };

  const updateConversationStatus = async (conversationId: string, newStatus: string) => {
    try {
      const token = Cookies.get("access_token");
      const res = await fetch(`/api/v1/conversations/${conversationId}/status`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        // Optimistically update local state
        setConversations(prev => prev.map(c => 
          c.id === conversationId ? { ...c, status: newStatus } : c
        ));
        if (activeConversation?.id === conversationId) {
          setActiveConversation(prev => prev ? { ...prev, status: newStatus } : null);
        }
      }
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const sendMessage = async () => {
    if (!replyText.trim() || !activeConversation || isSending) return;
    
    const content = replyText.trim();
    setReplyText("");
    setIsSending(true);

    const tempId = `temp-${Date.now()}`;
    const optimisticMsg: Message = {
      id: tempId,
      conversation_id: activeConversation.id,
      sender_type: 'human',
      content: content,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, optimisticMsg]);
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);

    try {
      const token = Cookies.get("access_token");
      const res = await fetch(`/api/v1/conversations/${activeConversation.id}/messages`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
      });
      
      if (res.ok) {
        const savedMsg = await res.json();
        setMessages(prev => prev.map(m => m.id === tempId ? savedMsg : m));
        // Auto-takeover
        if (activeConversation.status !== 'manual') {
          updateConversationStatus(activeConversation.id, 'manual');
        }
      } else {
        console.error("Failed to send message", await res.text());
        // Remove optimistic message on failure
        setMessages(prev => prev.filter(m => m.id !== tempId));
      }
    } catch (err) {
      console.error("Error sending message", err);
      setMessages(prev => prev.filter(m => m.id !== tempId));
    } finally {
      setIsSending(false);
      fetchConversations(); // Update list to bump conversation
    }
  };

  const markAsRead = async (conversationId: string) => {
    try {
      const token = Cookies.get("access_token");
      await fetch(`/api/v1/conversations/${conversationId}/read`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      });
      // Optimistically update local state
      setConversations(prev => prev.map(c => 
        c.id === conversationId ? { ...c, is_unread: false } : c
      ));
    } catch (err) {
      console.error("Failed to mark as read", err);
    }
  };

  useEffect(() => {
    if (!id) return;
    fetchConversations();
    // Swappable for WebSockets later
    const intervalId = setInterval(fetchConversations, CONVERSATION_POLL_MS);
    return () => clearInterval(intervalId);
  }, [id]);

  useEffect(() => {
    if (activeConversation) {
      fetchMessages(activeConversation.id);
      if (activeConversation.is_unread) {
        markAsRead(activeConversation.id);
      }
      // Swappable for WebSockets later
      const intervalId = setInterval(() => {
        fetchMessages(activeConversation.id);
      }, MESSAGE_POLL_MS);
      return () => clearInterval(intervalId);
    } else {
      setMessages([]);
    }
  }, [activeConversation]);

  if (isLoading) {
    return <div className="p-8 text-center text-on-surface-variant h-full flex items-center justify-center font-body-lg">Loading inbox...</div>;
  }

  return (
    <div className="flex flex-1 overflow-hidden bg-background text-on-surface w-full h-full">
      {/* Conversation List Sidebar */}
      <section className={`w-full md:w-80 border-r border-secondary-container bg-surface-bright flex flex-col h-full flex-shrink-0 ${activeConversation ? 'hidden md:flex' : 'flex'}`}>
        <div className="p-4 border-b border-secondary-container flex justify-between items-center bg-surface">
          <div className="flex items-center gap-2">
            <button onClick={() => router.push(`/dashboard/businesses/${id}`)} className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">arrow_back</button>
            <h3 className="font-headline-md text-[20px] font-semibold">Conversations</h3>
          </div>
          <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">filter_list</button>
        </div>
        
        <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-on-surface-variant font-body-md">No conversations yet.</div>
          ) : (
            conversations.map((conv) => {
              const isActive = activeConversation?.id === conv.id;
              return (
                <div 
                  key={conv.id} 
                  onClick={() => setActiveConversation(conv)}
                  className={`p-3 rounded-lg cursor-pointer border transition-colors flex flex-col gap-sm shadow-[0_4px_20px_-5px_rgba(0,0,0,0.04)] relative
                    ${isActive ? 'bg-surface-container border-transparent' : 'bg-transparent border-transparent hover:bg-surface-container-highest'}
                  `}
                >
                  {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-full"></div>}
                  
                  <div className={`flex justify-between items-start ${isActive ? 'ml-2' : ''}`}>
                    <div className="flex items-center gap-2 relative">
                      <span className={`material-symbols-outlined text-[18px] ${isActive ? 'text-primary' : 'text-on-surface-variant'}`}>
                        {conv.channel === 'whatsapp' ? 'chat' : 'send'}
                      </span>
                      <span className={`font-label-md text-label-md text-on-surface ${conv.is_unread ? 'font-bold' : 'font-medium'}`}>
                        {conv.customer_name || conv.customer_identifier}
                      </span>
                      {conv.is_unread && (
                        <span className="w-2 h-2 rounded-full bg-primary absolute -right-3 top-1"></span>
                      )}
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">
                      {format(new Date(conv.last_activity_at), 'HH:mm')}
                    </span>
                  </div>
                  
                  <div className={`flex items-center gap-2 ${isActive ? 'ml-2' : ''} mt-1`}>
                    <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm text-[10px] uppercase tracking-wider">
                      {conv.status === 'limit_reached' ? (
                        <Link href={`/dashboard/billing`} style={{ color: "red", fontWeight: "bold", textDecoration: "none" }}>Paused — Limit Reached</Link>
                      ) : conv.status === 'ai_handling' ? 'AI Handled' : conv.status === 'needs_human' ? 'Needs You' : 'Manual'}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full font-label-sm text-[10px] uppercase tracking-wider ${conv.channel === 'whatsapp' ? 'bg-[#dcf8c6] text-[#075e54]' : 'bg-[#e1f5fe] text-[#0277bd]'}`}>
                      {conv.channel}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* Main Content Area */}
      <section className={`flex-1 flex flex-col bg-background h-full relative ${!activeConversation ? 'hidden md:flex' : 'flex'}`}>
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <header className="h-16 px-md flex items-center justify-between border-b border-secondary-container bg-surface/80 backdrop-blur-sm z-10">
              <div className="flex items-center gap-md">
                <button 
                  onClick={() => setActiveConversation(null)}
                  className="md:hidden p-2 -ml-2 text-on-surface-variant hover:text-primary transition-colors"
                >
                  <span className="material-symbols-outlined">arrow_back</span>
                </button>
                <div className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface">
                  <span className="material-symbols-outlined text-[20px]">person</span>
                </div>
                <div>
                  <h2 className="font-headline-md text-[18px] font-semibold text-on-surface">
                    {activeConversation.customer_name || activeConversation.customer_identifier}
                  </h2>
                    <p className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-1">
                      <span className={`w-2 h-2 rounded-full ${activeConversation.status === 'ai_handling' ? 'bg-primary' : activeConversation.status === 'limit_reached' ? 'bg-red-500' : 'bg-on-surface-variant'} inline-block`}></span> 
                      {activeConversation.status === 'limit_reached' ? (
                        <Link href={`/dashboard/billing`} style={{ color: "red", fontWeight: "bold", textDecoration: "none" }}>Paused — Limit Reached</Link>
                      ) : activeConversation.status === 'ai_handling' ? 'AI Agent Active' : activeConversation.status === 'needs_human' ? 'Needs You' : 'Manual Mode'} on {activeConversation.channel === 'whatsapp' ? 'WhatsApp' : 'Telegram'}
                    </p>
                </div>
              </div>
              <div className="flex items-center gap-sm">
                <button 
                  onClick={() => updateConversationStatus(activeConversation.id, activeConversation.status === 'ai_handling' ? 'manual' : 'ai_handling')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-colors ${
                    activeConversation.status === 'ai_handling'
                      ? 'border-primary text-primary hover:bg-primary/5'
                      : 'border-secondary-container text-on-surface-variant hover:bg-surface-container'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {activeConversation.status === 'ai_handling' ? 'smart_toy' : 'person'}
                  </span>
                  {activeConversation.status === 'ai_handling' ? 'AI Enabled' : 'AI Disabled'}
                </button>
                <button className="p-2 rounded-lg hover:bg-surface-container-high text-on-surface-variant transition-colors"><span className="material-symbols-outlined">search</span></button>
                <button className="p-2 rounded-lg hover:bg-surface-container-high text-on-surface-variant transition-colors"><span className="material-symbols-outlined">more_vert</span></button>
              </div>
            </header>

            {/* Messages Canvas */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-md flex flex-col gap-lg w-full max-w-[container-max] mx-auto">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-on-surface-variant font-body-md">
                  No messages yet.
                </div>
              ) : (
                messages.map((msg, idx) => {
                  const isBusiness = msg.sender_type === 'ai' || msg.sender_type === 'human';
                  return (
                    <div key={msg.id} className={`flex flex-col gap-xs max-w-[85%] ${isBusiness ? 'self-end items-end' : 'self-start'}`}>
                      <div className={`flex items-end gap-2 ${isBusiness ? 'flex-row-reverse' : ''}`}>
                        {isBusiness ? (
                          <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center mb-1">
                            <span className="material-symbols-outlined text-on-primary-container text-[18px]">
                              {msg.sender_type === 'ai' ? 'smart_toy' : 'person'}
                            </span>
                          </div>
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center mb-1">
                            <span className="material-symbols-outlined text-on-surface text-[18px]">person</span>
                          </div>
                        )}
                        
                        <div className={`p-4 rounded-2xl shadow-[0_4px_20px_-5px_rgba(0,0,0,0.02)] ${
                          isBusiness 
                            ? 'bg-surface-container-low rounded-br-sm border border-secondary-container' 
                            : 'bg-surface-container-lowest border border-secondary-container rounded-bl-sm'
                        }`}>
                          <p className="font-body-md text-body-md text-on-surface leading-relaxed whitespace-pre-wrap">
                            {msg.content}
                          </p>
                        </div>
                      </div>
                      <span className={`font-label-sm text-[11px] text-on-surface-variant ${isBusiness ? 'mr-10' : 'ml-10'}`}>
                        {format(new Date(msg.created_at), 'HH:mm')} {isBusiness ? `• ${msg.sender_type === 'ai' ? 'AI Assistant' : 'You'}` : ''}
                      </span>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-md bg-background w-full max-w-[container-max] mx-auto">
              <div className="relative flex items-end gap-2 bg-surface-container-lowest border border-secondary-container rounded-xl p-2 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.04)] focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/20 transition-all duration-200">
                <button className="p-2 text-on-surface-variant hover:text-primary transition-colors self-end mb-1 cursor-not-allowed" disabled>
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <textarea 
                  className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-32 min-h-[44px] py-3 font-body-md text-body-md text-on-surface placeholder-on-surface-variant custom-scrollbar" 
                  placeholder="Type your reply..." 
                  rows={1}
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  disabled={isSending}
                ></textarea>
                <button 
                  className={`p-3 rounded-lg self-end flex items-center justify-center transition-colors ${
                    replyText.trim() && !isSending 
                      ? 'bg-primary text-on-primary hover:bg-primary/90' 
                      : 'bg-surface-container text-on-surface-variant cursor-not-allowed'
                  }`}
                  onClick={sendMessage}
                  disabled={!replyText.trim() || isSending}
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                    {isSending ? 'hourglass_empty' : 'send'}
                  </span>
                </button>
              </div>
              <div className="flex justify-between items-center mt-2 px-1">
                <span className="font-label-sm text-[11px] text-on-surface-variant flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">info</span> You are replying manually as the owner.
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] mb-4 opacity-20">chat</span>
            <p className="font-body-md">Select a conversation to view</p>
          </div>
        )}
      </section>
    </div>
  );
}
