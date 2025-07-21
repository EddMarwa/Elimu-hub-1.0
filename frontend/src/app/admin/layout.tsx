import React from "react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <nav className="bg-cyan-700 text-white px-8 py-4 flex gap-8">
        <a href="/admin" className="font-bold hover:underline">Dashboard</a>
        <a href="/admin/subjects" className="hover:underline">Subjects</a>
        <a href="/admin/documents" className="hover:underline">Documents</a>
      </nav>
      <main>{children}</main>
    </div>
  );
} 