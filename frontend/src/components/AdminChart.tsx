"use client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function AdminChart({ data, xKey, yKey, title }: {
  data: any[];
  xKey: string;
  yKey: string;
  title?: string;
}) {
  return (
    <div className="bg-white/80 dark:bg-[#23243a]/80 rounded-xl shadow-md p-6">
      {title && <div className="mb-2 font-semibold">{title}</div>}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Bar dataKey={yKey} fill="#06b6d4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
} 