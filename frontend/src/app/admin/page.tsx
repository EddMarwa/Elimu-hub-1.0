"use client";
import React, { useEffect, useState } from "react";
import AdminCard from "@/components/AdminCard";
import AdminChart from "@/components/AdminChart";
import { useRouter } from "next/navigation";
import { useFetch } from "@/hooks/useFetch";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export default function AdminDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const router = useRouter();
  const { data: topics, loading: topicsLoading } = useFetch<{ topics: { id: number; name: string }[] }>(`${API_BASE}/list-topics`, []);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/analytics/summary?hours=24`)
      .then((res) => res.json())
      .then(setSummary);
    fetch(`${API_BASE}/analytics/summary?hours=24`)
      .then((res) => res.json())
      .then((data) => {
        setChartData(
          (data.top_endpoints || []).map((ep: any) => ({
            endpoint: ep.endpoint,
            count: ep.count,
          }))
        );
      });
  }, []);

  useEffect(() => {
    if (topics && topics.topics.length > 0 && selectedTopicId === null) {
      setSelectedTopicId(topics.topics[0].id);
    }
  }, [topics]);

  return (
    <div className="min-h-screen py-8 px-4 md:px-16" style={{ background: "var(--background)", color: "var(--foreground)" }}>
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
        <AdminCard title="Subjects" value={summary?.unique_subjects ?? "-"} onClick={() => router.push("/admin/subjects")} />
        <AdminCard title="Documents" value={summary?.total_documents ?? "-"} onClick={() => router.push("/admin/documents")} />
        <AdminCard title="API Requests (24h)" value={summary?.total_requests ?? "-"} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <AdminChart data={chartData} xKey="endpoint" yKey="count" title="Top API Endpoints" />
      </div>
    </div>
  );
} 