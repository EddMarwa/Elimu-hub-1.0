"use client";
import { useEffect, useState } from "react";
import type { RecursivePartial, IOptions } from "tsparticles-engine";
import dynamic from "next/dynamic";
import Link from "next/link";

const Particles = dynamic(() => import("react-tsparticles"), { ssr: false });

export default function Home() {
  const [showParticles, setShowParticles] = useState(false);

  useEffect(() => {
    setShowParticles(true);
  }, []);

  const particlesOptions: RecursivePartial<IOptions> = {
    background: {
      color: { value: "transparent" },
    },
    fpsLimit: 60,
    particles: {
      number: { value: 18, density: { enable: true, area: 800 } },
      color: { value: ["#198754", "#FFD700", "#4CAF50"] },
      shape: {
        type: "image",
        image: [
          {
            src: "/file.svg",
            width: 20,
            height: 20,
          },
        ],
      },
      opacity: { value: 0.25 },
      size: { value: 24, random: { enable: true, minimumValue: 16 } },
      move: {
        enable: true,
        speed: 1.2,
        direction: "none" as const,
        random: true,
        straight: false,
        outModes: { default: 'out' },
      },
    },
    detectRetina: true,
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {showParticles && (
        <Particles
          id="tsparticles"
          options={particlesOptions}
          className="absolute inset-0 z-0"
        />
      )}
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
