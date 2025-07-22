import Link from "next/link";
import ClientOnly from "./components/ClientOnly";
import AnimatedBackground from "./components/AnimatedBackground";
import Navigation from "@/components/Navigation";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Navigation */}
      <Navigation />
      
      {/* Animated background elements - only render on client */}
      <ClientOnly>
        <AnimatedBackground />
      </ClientOnly>
      
      {/* Main content area without hero section */}
      <main className="relative z-10 min-h-screen">
        {/* Content can be added here as needed */}
      </main>
    </div>
  );
}
