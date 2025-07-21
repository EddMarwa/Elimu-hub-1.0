import React from "react";

export default function AdminCard({
  title,
  value,
  icon,
  onClick,
  className = "",
}: {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <div
      className={`flex flex-col items-start justify-between bg-white/80 dark:bg-[#23243a]/80 rounded-xl shadow-md p-6 cursor-pointer hover:shadow-lg transition ${className}`}
      onClick={onClick}
    >
      <div className="text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-2">
        {icon}
        <span>{title}</span>
      </div>
      <div className="text-3xl font-bold text-cyan-700 dark:text-cyan-300">{value}</div>
    </div>
  );
} 