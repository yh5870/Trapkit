import Plane from "./Plane";

export default function Loading({ label = "리스트를 만들고 있어요…" }: { label?: string }) {
  return (
    <div className="loading-screen" role="status">
      <div className="runway"><Plane className="flying-plane" /></div>
      <strong>{label}</strong>
      <span>여행 맥락에 맞춰 꼭 필요한 것만 고르는 중</span>
    </div>
  );
}