"use client";

export default function AnimatedBackground() {
  return (
    <div className="absolute inset-0 z-0">
      <div className="absolute top-20 left-10 w-4 h-4 bg-green-400 rounded-full animate-bounce opacity-60"></div>
      <div className="absolute top-32 right-20 w-6 h-6 bg-yellow-400 rounded-full animate-pulse opacity-50"></div>
      <div className="absolute bottom-40 left-32 w-5 h-5 bg-green-500 rounded-full animate-ping opacity-40"></div>
      <div className="absolute bottom-20 right-16 w-3 h-3 bg-yellow-500 rounded-full animate-bounce opacity-70"></div>
      <div className="absolute top-1/2 left-1/4 w-4 h-4 bg-green-300 rounded-full animate-pulse opacity-60"></div>
      <div className="absolute top-1/3 right-1/3 w-5 h-5 bg-yellow-300 rounded-full animate-ping opacity-50"></div>
    </div>
  );
}
