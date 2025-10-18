import React, { useEffect, useState } from 'react';

export default function TaskBoard({ projectId }) {
  const [cols, setCols] = useState({ todo: [], inprogress: [], done: [] });

  useEffect(() => {
    fetch(`/api/projects/${projectId}/tasks`)
      .then((r) => r.json())
      .then((tasks) => {
        const grouped = { todo: [], inprogress: [], done: [] };
        tasks.forEach((t) => {
          const s = t.status || 'todo';
          grouped[s] = grouped[s] || [];
          grouped[s].push(t);
        });
        setCols(grouped);
      })
      .catch((e) => console.warn('fetch tasks failed', e));
  }, [projectId]);

  return (
    <div className="grid grid-cols-3 gap-4">
      {['todo', 'inprogress', 'done'].map((col) => (
        <div key={col} className="p-3 border rounded bg-gray-50">
          <h3 className="font-bold mb-2">{col.toUpperCase()}</h3>
          {cols[col].map((t) => (
            <div key={t.id} className="mt-2 p-2 bg-white shadow-sm rounded">
              <div className="text-sm font-semibold">{t.title}</div>
              <div className="text-xs text-gray-600">{t.assignee?.display_name || 'Unassigned'}</div>
              <div className="text-xs mt-1">Estimate: {t.estimate_hours || '-' }h</div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
