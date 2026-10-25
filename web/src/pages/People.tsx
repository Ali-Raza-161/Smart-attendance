import { useEffect, useState } from 'react'
import { get, post } from '../services/api'
export default function People() {
  const [people, setPeople] = useState<any[]>([]); const [name, setName] = useState(''); const [roll, setRoll] = useState(''); const [consent, setConsent] = useState(false)
  function load() { get('/people').then(setPeople).catch(() => setPeople([])) }
  useEffect(load, [])
  async function add(e: React.FormEvent) { e.preventDefault(); await post('/people', { name, roll_or_employee_no: roll, consent }); setName(''); setRoll(''); load() }
  return <div><h1>People</h1><div className="card"><p className="notice">Written consent is required before enrollment (parent consent for minors). People who do not consent use manual attendance.</p>
    <form onSubmit={add}><input placeholder="Name" value={name} onChange={e => setName(e.target.value)} /><input placeholder="Roll / employee no" value={roll} onChange={e => setRoll(e.target.value)} /><label><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} /> Written consent recorded</label><button>Add person</button></form></div>
    <table><thead><tr><th>Name</th><th>Roll</th><th>Consent</th><th>Embeddings</th></tr></thead><tbody>{people.map((p: any) => <tr key={p.id}><td>{p.name}</td><td>{p.roll_or_employee_no}</td><td>{p.consent ? 'Yes' : 'No'}</td><td>{p.embedding_count}</td></tr>)}</tbody></table></div>
}
