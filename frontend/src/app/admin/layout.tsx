'use client';

import React from "react";
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

function AdminNavbar() {
  const { user, logout } = useAuth();
  
  return (
    <nav className="bg-cyan-700 text-white px-8 py-4 flex justify-between items-center">
      <div className="flex gap-8">
        <Link href="/admin" className="font-bold hover:underline">Dashboard</Link>
        <Link href="/admin/subjects" className="hover:underline">Subjects</Link>
        <Link href="/admin/documents" className="hover:underline">Documents</Link>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm">Welcome, {user?.email}</span>
        <button 
          onClick={logout}
          className="text-sm bg-cyan-600 px-3 py-1 rounded hover:bg-cyan-500"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requireAdmin={true}>
      <div>
        <AdminNavbar />
        <main>{children}</main>
      </div>
    </ProtectedRoute>
  );
} 