import { Routes, Route, Link, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import People from './pages/People'
import Enroll from './pages/Enroll'
import TakeAttendance from './pages/TakeAttendance'
import Reports from './pages/Reports'
function authed() { return !!localStorage.getItem('sa_token') }
function Guard({ children }: { children: JSX.Element }) { return authed() ? children : <Navigate to="/login" /> }
export default function App() {
  return <div className="shell"><nav><strong>Smart Attendance</strong><Link to="/dashboard">Dashboard</Link><Link to="/people">People</Link><Link to="/enroll">Enroll</Link><Link to="/attendance">Take Attendance</Link><Link to="/reports">Reports</Link><button onClick={() => { localStorage.removeItem('sa_token'); location.href = '/login' }}>Logout</button><p style={{ fontSize: 12, opacity: 0.8 }}>Educational demo. Consent required. Manual attendance always available.</p></nav>
    <main><Routes><Route path="/login" element={<Login />} /><Route path="/dashboard" element={<Guard><Dashboard /></Guard>} /><Route path="/people" element={<Guard><People /></Guard>} /><Route path="/enroll" element={<Guard><Enroll /></Guard>} /><Route path="/attendance" element={<Guard><TakeAttendance /></Guard>} /><Route path="/reports" element={<Guard><Reports /></Guard>} /><Route path="*" element={<Navigate to="/dashboard" />} /></Routes></main></div>
}
