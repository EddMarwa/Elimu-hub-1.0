'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function Navigation() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="absolute top-0 left-0 right-0 z-50 bg-black bg-opacity-20 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <Link 
            href="/" 
            className="text-white text-xl font-bold hover:text-yellow-200 transition-colors"
          >
            Elimu Hub AI
          </Link>
          
          <div className="flex items-center gap-6">
            <Link 
              href="/ai" 
              className="text-white hover:text-yellow-200 transition-colors"
            >
              AI Chat
            </Link>
            <Link 
              href="/chat" 
              className="text-white hover:text-yellow-200 transition-colors"
            >
              Knowledge Base
            </Link>
            
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                {user?.is_admin && (
                  <Link 
                    href="/admin" 
                    className="text-white hover:text-yellow-200 transition-colors"
                  >
                    Admin
                  </Link>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm">{user?.email}</span>
                  <button
                    onClick={logout}
                    className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <Link
                href="/auth/login"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
