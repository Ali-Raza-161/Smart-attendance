import { useState } from 'react'
import WebcamCapture from '../components/WebcamCapture'
import FaceBoxOverlay, { FaceBox } from '../components/FaceBoxOverlay'
import AttendanceTable, { Row } from '../components/AttendanceTable'
import { api, get } from '../services/api'
export default function TakeAttendance() {
  const [sessionId, setSessionId] = useState(''); const [boxes, setBoxes] = useState<FaceBox[]>([]); const [rows, setRows] = useState<Row[]>([]); const [msg, setMsg] = useState('')
  async function loadRows() { if (!sessionId) return; setRows(await get(`/sessions/${sessionId}/attendance`)) }
  async function recognize(file: File) { if (!sessionId) { setMsg('Enter a session ID first (create one from the API or Dashboard flow).'); return } const fd = new FormData(); fd.append('file', file); try { const d = await api.post(`/sessions/${sessionId}/recognize`, fd); setBoxes(d.data.faces || []); setMsg(d.data.note || ''); await loadRows() } catch (err: any) { setMsg(err.response?.data?.detail || 'Recognition failed.') } }
  return <div><h1>Take Attendance</h1><div className="card"><p>Review before saving: detected faces are shown below, and the teacher corrects present/absent/late in the table. Nothing is saved as present by the system alone.</p>
    <input placeholder="Session ID" value={sessionId} onChange={e => setSessionId(e.target.value)} /><button onClick={loadRows}>Load session table</button></div>
    <WebcamCapture onFile={recognize} /><FaceBoxOverlay boxes={boxes} />{msg && <p>{msg}</p>}
    <div className="card"><h2>Review table</h2><AttendanceTable rows={rows} onChanged={loadRows} /></div></div>
}
