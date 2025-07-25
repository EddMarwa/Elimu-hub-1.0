import Link from "next/link";
import ClientOnly from "./components/ClientOnly";
import AnimatedBackground from "./components/AnimatedBackground";

export default function Home() {
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background elements - only render on client */}
      <ClientOnly>
        <AnimatedBackground />
      </ClientOnly>
      
      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 py-24 sm:py-32">
        <h1 className="text-4xl sm:text-6xl font-extrabold text-center mb-4">
          <span className="text-white drop-shadow-lg">Elimu </span>
          <span className="bg-gradient-to-r from-yellow-200 via-white to-yellow-200 bg-clip-text text-transparent drop-shadow-lg">Hub</span>
          <span className="text-yellow-200 drop-shadow-lg"> AI</span>
        </h1>
        <p className="max-w-xl text-center text-lg sm:text-2xl text-white mb-8 drop-shadow-md">
          Build your knowledge base from PDFs and get intelligent responses powered by RAG technology. Upload documents, organize by topics, and chat with your content.
        </p>
        <div className="flex justify-center">
          <Link
            href="/chat"
            className="inline-block rounded-full bg-green-700 hover:bg-green-800 transition-colors text-white font-semibold px-12 py-4 text-xl shadow-lg transform hover:scale-105 transition-transform"
          >
            📚 Knowledge Base
          </Link>
        </div>
      </main>
      {/* Subtle grid overlay (not visible, just for layout) */}
      {/* You can add more sections below as needed */}
    </div>
  );
}
