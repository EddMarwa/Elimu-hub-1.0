"use client";
import React, { useEffect, useState } from "react";
import DataTable from "@/components/DataTable";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [editRow, setEditRow] = useState<any | null>(null);
  const [newName, setNewName] = useState("");

  const fetchSubjects = async () => {
    const res = await fetch(`${API_BASE}/list-topics`);
    const data = await res.json();
    setSubjects((data.topics || []).map((t: string) => ({ name: t })));
  };

  useEffect(() => { fetchSubjects(); }, []);

  const handleEdit = (row: any) => setEditRow(row);
  const handleDelete = async (row: any) => {
    if (!window.confirm(`Delete subject "${row.name}" and all its documents?`)) return;
    await fetch(`${API_BASE}/subjects/${encodeURIComponent(row.name)}`, { method: "DELETE" });
    fetchSubjects();
  };
  const handleSave = async () => {
    await fetch(`${API_BASE}/subjects/${encodeURIComponent(editRow.name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName }),
    });
    setEditRow(null);
    setNewName("");
    fetchSubjects();
  };

  return (
    <div className="py-8 px-4 md:px-16">
      <h2 className="text-2xl font-bold mb-6">Subjects</h2>
      <DataTable
        columns={[{ key: "name", label: "Subject Name" }]}
        data={subjects}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      {editRow && (
        <div className="mt-4">
          <input value={newName} onChange={e => setNewName(e.target.value)} className="p-2 border rounded mr-2" />
          <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded">Save</button>
          <button onClick={() => setEditRow(null)} className="ml-2 px-4 py-2 bg-gray-300 rounded">Cancel</button>
        </div>
      )}
    </div>
  );
} 