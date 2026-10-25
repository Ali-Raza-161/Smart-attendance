import { useEffect, useState } from 'react'
import { get } from '../services/api'
export default function Dashboard() {
  const [rows, setRows] = useState<any[]>([])
  useEffect(() => { get('/reports/attendance').then((d: any) => setRows(d.rows || [])).catch(() => setRows([])) }, [])
  const total = rows.length, present = rows.filter(r => r.status === 'present').length
  const low = rows.filter(r => r.status === 'absent')
  return <div><h1>Dashboard</h1><div className="card"><p>Today's attendance (all reports): <strong>{present} / {total} present</strong> ({total ? Math.round(100 * present / total) : 0}%)</p><p>Class percentage and low-attendance list come from the reports API.</p></div>
    <div className="card"><h2>Low attendance / absent</h2><ul>{low.slice(0, 10).map((r, i) => <li key={i}>{r.name} — {r.date} — {r.status}</li>)}</ul>{low.length === 0 && <p>No absent records yet.</p>}</div></div>
}
