'use client';

import Link from 'next/link';

export default function Navigation() {
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
          </div>
        </div>
      </div>
    </nav>
  );
}
