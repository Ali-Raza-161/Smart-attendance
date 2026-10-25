import { useEffect, useState } from 'react'
import { get, api } from '../services/api'
export default function Reports() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { get('/reports/attendance').then(setData).catch(() => setData(null)) }, [])
  async function exportXlsx() { const r = await api.get('/reports/export', { responseType: 'blob' }); const url = URL.createObjectURL(r.data); const a = document.createElement('a'); a.href = url; a.download = 'attendance.xlsx'; a.click() }
  return <div><h1>Reports</h1><div className="card"><p>Total: {data?.total ?? '—'} · Present: {data?.present ?? '—'} · {data?.percentage ?? '—'}%</p><button onClick={exportXlsx}>Export Excel</button>
    <table><thead><tr><th>Name</th><th>Date</th><th>Status</th></tr></thead><tbody>{(data?.rows || []).map((r: any) => <tr key={r.attendance_id}><td>{r.name}</td><td>{r.date}</td><td>{r.status}</td></tr>)}</tbody></table></div></div>
}
