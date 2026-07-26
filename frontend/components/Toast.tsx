export default function Toast({ children, action }: { children: React.ReactNode; action?: () => void }) {
  return (
    <div className="toast" role="status">
      <span>{children}</span>
      {action && <button onClick={action}>실행 취소</button>}
    </div>
  );
}