'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function AdminFloatingButton() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { user, isAuthenticated } = useAuth();

  // Only show for admin users
  if (!isAuthenticated || !user?.is_admin) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Button */}
      <div 
        className="relative group"
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
      >
        <Link
          href="/admin"
          className={`flex items-center gap-3 bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 hover:from-red-600 hover:via-orange-600 hover:to-yellow-600 text-white font-bold rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300 border-4 border-white ${
            isExpanded ? 'px-6 py-4' : 'w-14 h-14 justify-center'
          }`}
          title="Quick Admin Access"
        >
          <div className="relative">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2L3 7v11h4v-6h6v6h4V7l-7-5z" />
              <path d="M8 12h4v4H8v-4z" />
            </svg>
            {/* Pulsing indicator */}
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            </div>
          </div>
          
          {isExpanded && (
            <div className="flex flex-col">
              <span className="text-sm font-bold">ADMIN PANEL</span>
              <span className="text-xs opacity-90">Quick Access</span>
            </div>
          )}
        </Link>

        {/* Tooltip */}
        {!isExpanded && (
          <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-black text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            Admin Dashboard
            <div className="absolute top-full right-3 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-black"></div>
          </div>
        )}
      </div>
    </div>
  );
}
