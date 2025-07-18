"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function Home() {
  const [showParticles, setShowParticles] = useState(false);

  useEffect(() => {
    setShowParticles(true);
  }, []);

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background elements instead of particles */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-20 left-10 w-4 h-4 bg-green-400 rounded-full animate-bounce opacity-60"></div>
        <div className="absolute top-32 right-20 w-6 h-6 bg-yellow-400 rounded-full animate-pulse opacity-50"></div>
        <div className="absolute bottom-40 left-32 w-5 h-5 bg-green-500 rounded-full animate-ping opacity-40"></div>
        <div className="absolute bottom-20 right-16 w-3 h-3 bg-yellow-500 rounded-full animate-bounce opacity-70"></div>
        <div className="absolute top-1/2 left-1/4 w-4 h-4 bg-green-300 rounded-full animate-pulse opacity-60"></div>
        <div className="absolute top-1/3 right-1/3 w-5 h-5 bg-yellow-300 rounded-full animate-ping opacity-50"></div>
      </div>
      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 py-24 sm:py-32">
        <h1 className="text-4xl sm:text-6xl font-extrabold text-center mb-4">
          <span className="text-green-700">Elimu </span>
          <span className="bg-gradient-to-r from-yellow-400 via-green-500 to-green-700 bg-clip-text text-transparent">Hub</span>
          <span className="text-yellow-500"> AI</span>
        </h1>
        <p className="max-w-xl text-center text-lg sm:text-2xl text-gray-700 mb-8">
          Empowering Kenyan education with AI. Curriculum-aligned answers, lesson planning, and personalized learning for teachers and students.
        </p>
        <Link
          href="/chat"
          className="inline-block rounded-full bg-green-700 hover:bg-yellow-500 transition-colors text-white font-semibold px-8 py-3 text-lg shadow-lg"
        >
          Get Early Access
        </Link>
      </main>
      {/* Subtle grid overlay (not visible, just for layout) */}
      {/* You can add more sections below as needed */}
    </div>
  );
}
