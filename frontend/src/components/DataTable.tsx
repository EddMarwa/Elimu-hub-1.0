import React from "react";

export default function DataTable({
  columns,
  data,
  onEdit,
  onDelete,
}: {
  columns: { key: string; label: string }[];
  data: any[];
  onEdit?: (row: any) => void;
  onDelete?: (row: any) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse bg-white dark:bg-gray-900">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="border-b p-2 text-left">{col.label}</th>
            ))}
            {(onEdit || onDelete) && <th className="border-b p-2 text-left">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-cyan-50 dark:hover:bg-cyan-950">
              {columns.map((col) => (
                <td key={col.key} className="p-2">{row[col.key]}</td>
              ))}
              {(onEdit || onDelete) && (
                <td className="p-2">
                  {onEdit && <button className="text-blue-600 mr-2" onClick={() => onEdit(row)}>Edit</button>}
                  {onDelete && <button className="text-red-600" onClick={() => onDelete(row)}>Delete</button>}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 