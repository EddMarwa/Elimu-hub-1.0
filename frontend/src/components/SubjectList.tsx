import React from "react";

export default function SubjectList({
  subjects,
  selected,
  onSelect,
}: {
  subjects: string[];
  selected: string | null;
  onSelect: (s: string) => void;
}) {
  return (
    <div className="flex gap-4 flex-wrap">
      {subjects.map((subject) => (
        <div
          key={subject}
          className={`px-5 py-3 rounded-lg border cursor-pointer min-w-[120px] mb-2 ${
            selected === subject
              ? "bg-cyan-100 dark:bg-cyan-900 border-cyan-400"
              : "bg-gray-100 dark:bg-gray-800 border-gray-300"
          }`}
          onClick={() => onSelect(subject)}
        >
          <b>{subject}</b>
        </div>
      ))}
    </div>
  );
} 