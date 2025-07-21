"use client";
import React, { useEffect, useState } from "react";
import DataTable from "@/components/DataTable";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);

  const fetchDocuments = async () => {
    const res = await fetch(`${API_BASE}/list-documents`);
    const data = await res.json();
    setDocuments(data);
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleDelete = async (row: any) => {
    if (!window.confirm("Delete this document?")) return;
    await fetch(`${API_BASE}/delete-document/${row.id}`, { method: "DELETE" });
    fetchDocuments();
  };

  return (
    <div className="py-8 px-4 md:px-16">
      <h2 className="text-2xl font-bold mb-6">Documents</h2>
      <DataTable
        columns={[
          { key: "file_name", label: "File Name" },
          { key: "topic", label: "Subject" },
          { key: "file_size_mb", label: "Size (MB)" },
          { key: "page_count", label: "Pages" },
          { key: "date_uploaded", label: "Uploaded" },
        ]}
        data={documents}
        onDelete={handleDelete}
      />
    </div>
  );
} 