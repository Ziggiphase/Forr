"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Cookies from "js-cookie";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function AnalyticsDashboardPage() {
  const params = useParams();
  const { id } = params as { id: string };

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState<any>(null);
  const [days, setDays] = useState(7);
  const [businessName, setBusinessName] = useState("");

  const fetchData = async () => {
    setLoading(true);
    const token = Cookies.get("access_token");
    try {
      const [bizRes, analyticsRes] = await Promise.all([
        fetch('/api/v1/businesses/' + id, {
          headers: { Authorization: 'Bearer ' + token },
        }),
        fetch('/api/v1/businesses/' + id + '/analytics?days=' + days, {
          headers: { Authorization: 'Bearer ' + token },
        }),
      ]);

      if (!bizRes.ok) throw new Error("Failed to fetch business");
      if (!analyticsRes.ok) throw new Error("Failed to fetch analytics");

      const bizData = await bizRes.json();
      setBusinessName(bizData.name);

      const analyticsData = await analyticsRes.json();
      setData(analyticsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id, days]);

  if (loading && !data) {
    return <div className="p-8">Loading Analytics...</div>;
  }
  if (error) {
    return <div className="p-8 text-error">{error}</div>;
  }
  if (!data) return null;

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("en-US").format(num);
  };

  const formatPercentage = (num: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "percent",
      maximumFractionDigits: 1,
    }).format(num);
  };

  const formatSeconds = (secs: number) => {
    if (!secs) return "N/A";
    if (secs < 60) return Math.round(secs) + "s";
    return (secs / 60).toFixed(1) + "m";
  };

  return (
    <div className="min-h-screen bg-background text-on-surface p-md md:p-lg flex flex-col gap-lg font-body-md custom-scrollbar">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-md">
        <div>
          <Link
            href={'/dashboard/businesses/' + id}
            className="text-primary hover:underline font-label-md flex items-center gap-1 mb-2"
          >
            <span className="material-symbols-outlined text-[16px]">arrow_back</span>
            Back to {businessName}
          </Link>
          <h1 className="font-headline-lg text-headline-lg font-bold">Analytics Dashboard</h1>
          <p className="text-on-surface-variant font-body-md mt-1">
            Track performance and insights for your AI agent.
          </p>
        </div>
        <div className="flex bg-surface-container-low rounded-lg p-1 border border-secondary-container shadow-sm">
          {[1, 7, 30].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={'px-4 py-2 rounded-md font-label-md transition-colors ' + (days === d ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant hover:bg-surface-container-highest")}
            >
              {d === 1 ? "Today" : d + " Days"}
            </button>
          ))}
        </div>
      </div>

      {/* Headline Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md">
        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <p className="text-on-surface-variant font-label-md mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">forum</span>
            Total Conversations
          </p>
          <p className="font-display text-display">{formatNumber(data.total_conversations)}</p>
        </div>
        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <p className="text-on-surface-variant font-label-md mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">escalator_warning</span>
            Escalation Rate
          </p>
          <p className="font-display text-display">{formatPercentage(data.escalation_rate)}</p>
          <p className="text-label-sm text-on-surface-variant mt-1">
            Chats needing human intervention
          </p>
        </div>
        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <p className="text-on-surface-variant font-label-md mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">timer</span>
            Avg Response Time
          </p>
          <div className="flex gap-4 items-baseline mt-2">
            <div>
              <p className="font-headline-md font-bold">{formatSeconds(data.response_time.ai_avg_seconds)}</p>
              <p className="text-label-sm text-on-surface-variant">AI</p>
            </div>
            <div className="w-px h-8 bg-secondary-container"></div>
            <div>
              <p className="font-headline-md font-bold">{formatSeconds(data.response_time.manual_avg_seconds)}</p>
              <p className="text-label-sm text-on-surface-variant">Manual</p>
            </div>
          </div>
        </div>
        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <p className="text-on-surface-variant font-label-md mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">thumb_up</span>
            Customer Satisfaction
          </p>
          <div className="flex gap-4 items-baseline mt-2">
            <div>
              <p className="font-headline-md font-bold text-primary">{data.satisfaction.thumbs_up}</p>
              <p className="text-label-sm text-on-surface-variant">?? Helpful</p>
            </div>
            <div className="w-px h-8 bg-secondary-container"></div>
            <div>
              <p className="font-headline-md font-bold text-error">{data.satisfaction.thumbs_down}</p>
              <p className="text-label-sm text-on-surface-variant">?? Unhelpful</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-md">
        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <h3 className="font-headline-md text-[18px] font-semibold mb-4">Activity Overview</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.activity}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e1dfdb" />
                <XAxis dataKey="date" stroke="#74746f" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#74746f" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e1dfdb" }}
                />
                <Legend wrapperStyle={{ fontSize: "14px", paddingTop: "10px" }} />
                <Line type="monotone" name="Total Chats" dataKey="total" stroke="#543ae5" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" name="Unique Customers" dataKey="unique" stroke="#1c1b1b" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-surface border border-secondary-container rounded-xl p-md shadow-sm">
          <h3 className="font-headline-md text-[18px] font-semibold mb-4">Token Spend Over Time</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.token_spend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e1dfdb" vertical={false} />
                <XAxis dataKey="date" stroke="#74746f" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#74746f" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                  cursor={{ fill: "#f6f3f2" }}
                  contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e1dfdb" }}
                />
                <Legend wrapperStyle={{ fontSize: "14px", paddingTop: "10px" }} />
                <Bar name="Tokens Used" dataKey="tokens" fill="#543ae5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
