import { useRef, useState } from 'react'
// Native webcam API (no react-webcam dependency required). File upload is
// the fallback when the camera is unavailable or permission is denied.
export default function WebcamCapture({ onFile }: { onFile: (f: File) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)
  async function start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) { videoRef.current.srcObject = stream; setRunning(true) }
    } catch { setError('Camera unavailable or permission denied. Use file upload instead.') }
  }
  return <div className="card">
    <p><strong>Camera</strong> — used only for this attendance session, with consent. A manual attendance option is always available.</p>
    <video ref={videoRef} autoPlay playsInline width={480} style={{ maxWidth: '100%', background: '#000' }} />
    <div><button onClick={start}>Start camera</button>{' '}
    <label>or upload a class photo: <input type="file" accept="image/png,image/jpeg" onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f) }} /></label></div>
    {running && <p>Camera running. Take a photo with your device, then upload it for review.</p>}
    {error && <p>{error}</p>}
  </div>
}
