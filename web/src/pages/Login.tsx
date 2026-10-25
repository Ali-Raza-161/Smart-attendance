import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { post } from '../services/api'
export default function Login() {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [err, setErr] = useState('')
  const nav = useNavigate()
  async function submit(e: React.FormEvent) { e.preventDefault(); try { const d = await post('/auth/login', { email, password }); localStorage.setItem('sa_token', d.token); localStorage.setItem('sa_user', JSON.stringify(d.user)); nav('/dashboard') } catch { setErr('Login failed. Check credentials and that the API is running.') } }
  return <div className="card"><h1>Login</h1><p className="notice">Admin and teacher sign in. No default account is shipped — create one with scripts_create_admin.py (see README).</p>
    <form onSubmit={submit}><input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /><br /><input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} /><br /><button>Login</button></form>{err && <p>{err}</p>}</div>
}
