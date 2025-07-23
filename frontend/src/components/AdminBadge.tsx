'use client';

import React from 'react';
import Link from 'next/link';

interface AdminBadgeProps {
  className?: string;
}

export default function AdminBadge({ className = '' }: AdminBadgeProps) {
  return (
    <Link 
      href="/admin" 
      className={`group inline-flex items-center gap-2 bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 hover:from-red-600 hover:via-orange-600 hover:to-yellow-600 text-white px-4 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 border-2 border-white/20 ${className}`}
      title="Access Admin Panel"
    >
      <div className="relative">
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
        </svg>
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full flex items-center justify-center">
          <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      <span className="text-sm">ADMIN</span>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
      </div>
    </Link>
  );
}
