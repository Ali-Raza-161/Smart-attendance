import { patch } from '../services/api'
export type Row = { id: number; name: string | null; status: string; confidence: number | null; marked_by: string }
export default function AttendanceTable({ rows, onChanged }: { rows: Row[]; onChanged: () => void }) {
  async function setStatus(id: number, status: string) { await patch(`/attendance/${id}`, { status }); onChanged() }
  return <table><thead><tr><th>Name</th><th>Status</th><th>Confidence</th><th>Marked by</th><th>Correct</th></tr></thead>
    <tbody>{rows.map(r => <tr key={r.id}><td>{r.name || '—'}</td><td>{r.status}</td><td>{r.confidence ?? '—'}</td><td>{r.marked_by}</td>
    <td><button onClick={() => setStatus(r.id, 'present')}>Present</button>{' '}<button onClick={() => setStatus(r.id, 'absent')}>Absent</button>{' '}<button onClick={() => setStatus(r.id, 'late')}>Late</button></td></tr>)}</tbody></table>
}
