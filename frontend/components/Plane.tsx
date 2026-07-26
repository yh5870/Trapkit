export default function Plane({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path d="M21.7 13.1 13 9.7V3.8c0-1-.5-2.3-1-2.3s-1 1.3-1 2.3v5.9l-8.7 3.4c-.5.2-.8.7-.8 1.2v.8l9.5-1.7v5.4l-2.6 1.6v1.1l3.6-.7 3.6.7v-1.1L13 18.8v-5.4l9.5 1.7v-.8c0-.5-.3-1-.8-1.2Z" fill="currentColor" />
    </svg>
  );
}