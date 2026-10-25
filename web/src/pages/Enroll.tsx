import { useState } from 'react'
import { api } from '../services/api'
export default function Enroll() {
  const [personId, setPersonId] = useState(''); const [files, setFiles] = useState<FileList | null>(null); const [msg, setMsg] = useState('')
  async function submit(e: React.FormEvent) { e.preventDefault(); if (!files) return; const fd = new FormData(); Array.from(files).forEach(f => fd.append('files', f)); try { const d = await api.post(`/people/${personId}/enroll`, fd); setMsg(JSON.stringify(d.data)) } catch (err: any) { setMsg(err.response?.data?.detail || 'Enrollment failed. A face model must be available; without it the API returns 503 and stores nothing.') } }
  return <div><h1>Enroll faces</h1><div className="card"><p>Upload 5–10 photos per person from different angles: look straight, left, right. Raw photos are <strong>not stored</strong> — only embeddings are stored, and only when a model is available.</p>
    <form onSubmit={submit}><input placeholder="Person ID" value={personId} onChange={e => setPersonId(e.target.value)} /><input type="file" multiple accept="image/png,image/jpeg" onChange={e => setFiles(e.target.files)} /><button>Enroll</button></form>{msg && <p>{msg}</p>}</div></div>
}
