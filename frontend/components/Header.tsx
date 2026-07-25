import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/api/auth";

function Plane({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path d="M21.7 13.1 13 9.7V3.8c0-1-.5-2.3-1-2.3s-1 1.3-1 2.3v5.9l-8.7 3.4c-.5.2-.8.7-.8 1.2v.8l9.5-1.7v5.4l-2.6 1.6v1.1l3.6-.7 3.6.7v-1.1L13 18.8v-5.4l9.5 1.7v-.8c0-.5-.3-1-.8-1.2Z" fill="currentColor" />
    </svg>
  );
}

export default function Header({ route }: { route: string }) {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useAuth();
  const go = (path: string) => router.push(path);

  return (
    <header className="site-header">
      <button className="brand" onClick={() => go("/")} aria-label="트립킷 홈">
        <span className="brand-mark"><Plane /></span>
        <span>트립킷</span>
      </button>
      <nav aria-label="주요 메뉴">
        {[["/", "리스트 만들기"], ["/baggage", "수화물 체커"], ["/trips", "내 여행"]].map(([path, label]) => (
          <button key={path} className={route === path ? "active" : ""} onClick={() => go(path)}>{label}</button>
        ))}
      </nav>
      <div className="account">
        {loggedIn ? (
          <>
            <button onClick={() => go("/trips")}>
              내 여행
            </button>

            <button
              onClick={() => {
                setLoggedIn(false);
                go("/");
              }}
            >
              로그아웃
            </button>
          </>
        ) : (
          <button
            className="login-link"
            onClick={() => go("/login")}
          >
            로그인
          </button>
        )}
      </div>
    </header>
  );
}