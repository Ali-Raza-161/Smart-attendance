export type FaceBox = { x: number; y: number; width: number; height: number }
export default function FaceBoxOverlay({ boxes }: { boxes: FaceBox[] }) {
  return <div className="card"><h3>Detected faces: {boxes.length}</h3>
    {boxes.length === 0 && <p>No face boxes to show. If a model is not available, recognition returns 503 and nothing is marked — teacher review is required.</p>}
    <ul>{boxes.map((b, i) => <li key={i}>Face {i + 1}: x={b.x}, y={b.y}, {b.width}×{b.height}</li>)}</ul>
  </div>
}
