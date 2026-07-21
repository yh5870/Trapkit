"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import homeData from "../data/routes/home.json";
import tripData from "../data/routes/trip.json";
import baggageData from "../data/routes/baggage.json";
import tripsData from "../data/routes/trips.json";
import authData from "../data/routes/auth.json";

type TripItem = (typeof tripData.view.categories)[number]["items"][number];
type Category = { name: string; items: TripItem[] };
type Verdict = (typeof baggageData.view.verdicts)[number] | typeof baggageData.view.aiFallback;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function Plane({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path d="M21.7 13.1 13 9.7V3.8c0-1-.5-2.3-1-2.3s-1 1.3-1 2.3v5.9l-8.7 3.4c-.5.2-.8.7-.8 1.2v.8l9.5-1.7v5.4l-2.6 1.6v1.1l3.6-.7 3.6.7v-1.1L13 18.8v-5.4l9.5 1.7v-.8c0-.5-.3-1-.8-1.2Z" fill="currentColor" />
    </svg>
  );
}

function EyebrowPlane() {
  return (
    <span className="eyebrow-plane" aria-hidden="true">
      <svg width="20" height="16" viewBox="0 0 24 18" aria-hidden="true">
        <line x1="0" y1="14" x2="24" y2="14" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.3" strokeDasharray="4 2" />
        <path d="M3 10l4-2 4 3 5-3 3 2" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.4" />
        <path d="M2 9l2.5-1 3 2 3.5-2 2 1 3-1.5 2 1 2.5-1" fill="currentColor" opacity="0.6" />
      </svg>
    </span>
  );
}

function useAuth() {
  const [loggedIn, setLoggedInState] = useState(false);
  useEffect(() => setLoggedInState(localStorage.getItem("tripkit-auth") === "1"), []);
  const setLoggedIn = (value: boolean) => {
    localStorage.setItem("tripkit-auth", value ? "1" : "0");
    setLoggedInState(value);
    window.dispatchEvent(new Event("tripkit-auth"));
  };
  useEffect(() => {
    const sync = () => setLoggedInState(localStorage.getItem("tripkit-auth") === "1");
    window.addEventListener("tripkit-auth", sync);
    return () => window.removeEventListener("tripkit-auth", sync);
  }, []);
  return [loggedIn, setLoggedIn] as const;
}

function Header({ route }: { route: string }) {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useAuth();
  const [menu, setMenu] = useState(false);
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
            <button className="account-button" onClick={() => setMenu(!menu)}>여행자 <span>⌄</span></button>
            {menu && <button className="account-menu" onClick={() => { setLoggedIn(false); setMenu(false); }}>로그아웃</button>}
          </>
        ) : <button className="login-link" onClick={() => go("/login")}>로그인</button>}
      </div>
    </header>
  );
}

function Shell({ route, children, narrow = false }: { route: string; children: React.ReactNode; narrow?: boolean }) {
  return <><Header route={route} /><main className={narrow ? "page narrow" : "page"}>{children}</main></>;
}

function Loading({ label = "리스트를 만들고 있어요…" }: { label?: string }) {
  return (
    <div className="loading-screen" role="status">
      <div className="runway"><Plane className="flying-plane" /></div>
      <strong>{label}</strong>
      <span>여행 맥락에 맞춰 꼭 필요한 것만 고르는 중</span>
    </div>
  );
}

function Toast({ children, action }: { children: React.ReactNode; action?: () => void }) {
  return <div className="toast" role="status"><span>{children}</span>{action && <button onClick={action}>실행 취소</button>}</div>;
}

function Home() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [destination, setDestination] = useState("");
  const [purposes, setPurposes] = useState<string[]>([]);
  const [optional, setOptional] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [customPurpose, setCustomPurpose] = useState("");
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const placeholders = ["예: 일본 삿포로, 다낭, 제주도", "예: 오사카, 방콕, 싱가포르", "예: 뉴욕, 파리, 런던"];

  useEffect(() => {
    if (!isInputFocused && !destination) {
      const interval = setInterval(() => setPlaceholderIndex((prev) => (prev + 1) % placeholders.length), 3000);
      return () => clearInterval(interval);
    }
  }, [isInputFocused, destination]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!destination.trim()) return setError("목적지를 입력해 주세요.");
    setError(""); setLoading(true);
    sessionStorage.setItem("tripkit-destination", destination.trim());
    await delay(1500);
    router.push("/trip");
  };
  const baggage = (item?: string) => router.push(`/baggage${item ? `?item=${encodeURIComponent(item)}` : ""}`);

  if (loading) return <Shell route="/"><Loading /></Shell>;
  return (
    <Shell route="/">
      <section className="home-hero">
        <div className="hero-copy">
          <p className="eyebrow">YOUR TRIP, PACKED RIGHT <EyebrowPlane /></p>
          <h1>가방을 열기 전에,<br /><em>여행을 먼저 담아요.</em></h1>
          <p>{homeData.page.tagline}. 블로그를 뒤지는 대신 이번 여행에 맞는 준비를 바로 시작하세요.</p>
        </div>
        <div className="route-stamp" aria-hidden="true">
          <span>ICN</span><i><Plane /></i><span>CTS</span>
          <small>DEC · SNOW ROUTE</small>
        </div>
      </section>

      <form className="planner-card" onSubmit={submit}>
        <div className="card-index"><span>01</span><p>여행의 방향</p></div>
        <div className="planner-body">
          <label className="field-label" htmlFor="destination">{homeData.page.prompt}</label>
          <div className={`destination-field ${error ? "invalid" : ""}`}>
            <span className="pin">●</span>
            <input
              id="destination"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder={isInputFocused || destination ? homeData.view.placeholders.destination : placeholders[placeholderIndex]}
              onFocus={() => setIsInputFocused(true)}
              onBlur={() => setIsInputFocused(false)}
            />
            <span className="airport-code">DESTINATION</span>
          </div>
          {error && <p className="field-error">{error}</p>}

          <fieldset>
            <legend>어떤 여행인가요?</legend>
            <div className="chips">
              {homeData.view.purposeChips.map((purpose, index) => <button type="button" key={purpose} className={purposes.includes(purpose) ? "selected" : ""} style={{ animationDelay: `${index * 60}ms` }} onClick={() => setPurposes((current) => current.includes(purpose) ? current.filter((item) => item !== purpose) : [...current, purpose])}>{purpose}</button>)}
              <input aria-label="여행 목적 직접 입력" placeholder="직접 입력 +" value={customPurpose} onChange={(e) => setCustomPurpose(e.target.value)} />
            </div>
            {!purposes.length && !customPurpose && <p className="helper">선택하지 않으면 일반 관광 기준으로 만들어요.</p>}
          </fieldset>

          <button type="button" className="optional-toggle" onClick={() => setOptional(!optional)} aria-expanded={optional}><span>{optional ? "−" : "+"}</span> 기간 · 출발 시기 · 동행 입력 <small>선택</small></button>
          {optional && <div className="optional-grid">
            <label>{homeData.view.optionalFields.durationLabel}<select defaultValue="4박 5일"><option>2박 3일</option><option>3박 4일</option><option>4박 5일</option><option>직접 입력</option></select></label>
            <label>{homeData.view.optionalFields.monthLabel}<input type="month" defaultValue="2026-12" /></label>
            <label>동행<select defaultValue="친구"><option>혼자</option><option>커플</option><option>친구</option><option>가족·유아 동반</option></select></label>
          </div>}
          <button className="primary cta" type="submit"><span>내 여행 리스트 만들기</span><span aria-hidden="true">→</span></button>
        </div>
      </form>

      <section className="home-grid">
        {loggedIn && <div className="recent-section">
          <div className="section-heading"><p className="eyebrow">CONTINUE PACKING</p><h2>최근 여행</h2></div>
          <div className="recent-list">{homeData.view.recentTrips.map((trip, index) => <button key={trip.id} onClick={() => router.push("/trip")}><span className="trip-number">0{index + 1}</span><span><strong>{trip.title}</strong><small>{trip.meta}</small></span><b>→</b></button>)}</div>
        </div>}
        <button className="baggage-shortcut" onClick={() => baggage()}>
          <span className="luggage-handle" />
          <span className="eyebrow">BAGGAGE QUICK CHECK</span>
          <strong>{homeData.view.baggageShortcut.title}</strong>
          <span>{homeData.view.baggageShortcut.subtitle} <b>→</b></span>
          <span className="mini-chips">{homeData.view.baggageShortcut.popularChips.slice(0, 3).map((chip) => <i key={chip} onClick={(e) => { e.stopPropagation(); baggage(chip); }}>{chip}</i>)}</span>
        </button>
      </section>
    </Shell>
  );
}

function Trip() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [categories, setCategories] = useState<Category[]>(tripData.view.categories as Category[]);
  const [tab, setTab] = useState("체크리스트");
  const [title, setTitle] = useState(tripData.page.tripTitle);
  const [editingTitle, setEditingTitle] = useState(false);
  const [adding, setAdding] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [deleted, setDeleted] = useState<{ category: number; item: TripItem } | null>(null);
  const [sheet, setSheet] = useState<"login" | "regenerate" | null>(null);
  const [loading, setLoading] = useState(false);
  const [memo, setMemo] = useState("");
  const [memos, setMemos] = useState([...tripData.view.memos]);
  const [regenerateMode, setRegenerateMode] = useState("keep");
  const total = categories.reduce((sum, category) => sum + category.items.length, 0);
  const checked = categories.reduce((sum, category) => sum + category.items.filter((item) => item.checked).length, 0);
  const percent = Math.round((checked / Math.max(total, 1)) * 100);

  useEffect(() => { const stored = sessionStorage.getItem("tripkit-title"); if (stored) setTitle(stored); }, []);
  const toggle = (id: string) => setCategories((current) => current.map((category) => ({ ...category, items: category.items.map((item) => item.id === id ? { ...item, checked: !item.checked } : item) })));
  const add = (categoryName: string, name: string) => {
    if (!name.trim()) return;
    setCategories((current) => current.map((category) => category.name === categoryName ? { ...category, items: [...category.items, { id: `user-${Date.now()}`, name: name.trim(), quantity: null, tip: null, baggageFlag: null, source: "user", checked: false } as TripItem] } : category));
    setAdding(null);
  };
  const remove = (categoryIndex: number, item: TripItem) => {
    setCategories((current) => current.map((category, index) => index === categoryIndex ? { ...category, items: category.items.filter((value) => value.id !== item.id) } : category));
    setDeleted({ category: categoryIndex, item }); setToast("항목을 삭제했어요");
  };
  const undo = () => {
    if (!deleted) return;
    setCategories((current) => current.map((category, index) => index === deleted.category ? { ...category, items: [...category.items, deleted.item] } : category));
    setDeleted(null); setToast(null);
  };
  const regenerate = async () => {
    const userItems = categories.flatMap((category) => category.items.filter((item) => item.source === "user").map((item) => ({ category: category.name, item })));
    setSheet(null); setLoading(true); await delay(1500);
    const fresh = structuredClone(tripData.view.categories) as Category[];
    if (regenerateMode === "keep") userItems.forEach(({ category, item }) => { const target = fresh.find((value) => value.name === category); if (target && !target.items.some((value) => value.id === item.id)) target.items.push(item); });
    setCategories(fresh); setLoading(false); setToast("리스트를 새로 만들었어요");
  };
  const save = () => loggedIn ? setToast("저장됨") : setSheet("login");
  const addMemo = () => { if (!memo.trim()) return; setMemos([{ id: `m-${Date.now()}`, content: memo.trim(), updatedAt: "방금" }, ...memos]); setMemo(""); setTimeout(() => setToast("저장됨"), 1000); };

  if (loading) return <Shell route="/trip"><Loading /></Shell>;
  return (
    <Shell route="/trip">
      <section className="trip-head">
        <p className="eyebrow">PACKING LIST · CTS</p>
        <div className="trip-title-row">
          <div>{editingTitle ? <input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} onBlur={() => setEditingTitle(false)} onKeyDown={(e) => e.key === "Enter" && setEditingTitle(false)} /> : <h1 onClick={() => setEditingTitle(true)}>{title} <small>✎</small></h1>}<p>{tripData.page.meta}</p></div>
          <div className="progress-copy"><strong>{checked}<span>/{total}</span></strong><small>{percent}% 준비 완료</small></div>
        </div>
        <div className={`progress-track ${percent >= 80 ? "high-progress" : ""}`}><span style={{ width: `${percent}%` }} /></div>
      </section>

      <div className="tabs" role="tablist">{tripData.view.tabs.map((value) => <button role="tab" aria-selected={tab === value} className={tab === value ? "active" : ""} key={value} onClick={() => setTab(value)}>{value}{value === "체크리스트" && <span>{total}</span>}</button>)}</div>

      {tab === "체크리스트" && <div className="trip-layout">
        <section className="checklist">
          {categories.map((category, categoryIndex) => {
            const count = category.items.filter((item) => item.checked).length;
            return <details className="category" key={category.name} open={categoryIndex < 2}>
              <summary><span>{category.name}</span><small>{count}/{category.items.length}</small><i>⌄</i></summary>
              <div className="items">{category.items.map((item) => <div className={`check-item ${item.checked ? "done" : ""}`} key={item.id}>
                <button className="checkbox" onClick={() => toggle(item.id)} aria-label={`${item.name} ${item.checked ? "체크 해제" : "체크"}`}>{item.checked && "✓"}</button>
                <div className="item-copy"><div><strong>{item.name}</strong>{item.quantity && <span>{item.quantity}</span>}{item.source === "user" && <em>내가 추가</em>}</div>{item.tip && <small>{item.tip}</small>}</div>
                {item.baggageFlag && <button className="baggage-badge" onClick={() => router.push(`/baggage?item=${encodeURIComponent(item.name)}`)}>⚠ {item.baggageFlag === "carry_on_only" ? "기내만" : "규정"}</button>}
                <button className="delete-item" onClick={() => remove(categoryIndex, item)} aria-label={`${item.name} 삭제`}>×</button>
              </div>)}</div>
              {adding === category.name ? <form className="add-item" onSubmit={(e) => { e.preventDefault(); add(category.name, new FormData(e.currentTarget).get("item") as string); }}><input name="item" autoFocus placeholder="준비물 이름" /><button>추가</button><button type="button" onClick={() => setAdding(null)}>취소</button></form> : <button className="add-link" onClick={() => setAdding(category.name)}>+ 항목 추가</button>}
            </details>;
          })}
        </section>
        <aside className="baggage-summary">
          <span className="summary-icon">!</span><p className="eyebrow">BAGGAGE ALERT</p><h2>확인할 수화물<br />규정이 {tripData.view.baggageSummary.length}건 있어요</h2>
          {tripData.view.baggageSummary.map((item) => <button key={item.item} onClick={() => router.push(`/baggage?item=${encodeURIComponent(item.item)}`)}><strong>{item.item}</strong><span>{item.rule}</span><b>→</b></button>)}
        </aside>
      </div>}

      {tab === "주의사항" && <section className="caution-grid">{tripData.view.cautions.map((caution) => <article key={caution.category}><div><span>{caution.category}</span>{caution.confidence === "check_required" && <em>출발 전 확인</em>}</div><p>{caution.text}</p></article>)}<div className="notice"><strong>꼭 확인하세요</strong><p>{tripData.view.cautionNotice}</p></div></section>}

      {tab === "메모" && <section className="memo-layout"><form onSubmit={(e) => { e.preventDefault(); addMemo(); }}><label htmlFor="memo">여행 전에 기억할 것</label><textarea id="memo" value={memo} onChange={(e) => setMemo(e.target.value)} placeholder="예약 번호, 이동 방법, 꼭 가볼 곳을 적어두세요." /><button className="primary">메모 추가</button></form><div className="memo-list">{memos.map((value) => <article key={value.id}><p>{value.content}</p><small>{value.updatedAt}</small><button onClick={() => setMemos(memos.filter((memoItem) => memoItem.id !== value.id))}>삭제</button></article>)}</div></section>}

      <div className="trip-actions"><button className="secondary" onClick={() => setSheet("regenerate")}>↻ 다시 생성</button><button className="primary" onClick={save}>리스트 저장</button></div>
      {toast && <Toast action={deleted ? undo : undefined}>{toast}</Toast>}
      {sheet && <div className="overlay" onClick={() => setSheet(null)}><section className="sheet" onClick={(e) => e.stopPropagation()}><span className="sheet-handle" />{sheet === "login" ? <><p className="eyebrow">SAVE YOUR TRIP</p><h2>리스트를 저장하려면<br />로그인이 필요합니다.</h2><p>지금 만든 리스트는 로그인 후 그대로 저장돼요.</p><button className="primary" onClick={() => { localStorage.setItem("tripkit-return", "/trip"); router.push("/login"); }}>로그인하기</button></> : <><p className="eyebrow">REBUILD LIST</p><h2>어떻게 다시 만들까요?</h2><label><input type="radio" name="regenerate" checked={regenerateMode === "keep"} onChange={() => setRegenerateMode("keep")} /><span><strong>내 항목은 유지하기</strong><small>내가 추가한 항목을 빼고 새로 받아요.</small></span></label><label><input type="radio" name="regenerate" checked={regenerateMode === "all"} onChange={() => setRegenerateMode("all")} /><span><strong>전체 새로 받기</strong><small>모든 항목을 처음부터 다시 만들어요.</small></span></label><button className="primary" onClick={regenerate}>다시 만들기</button></>}</section></div>}
    </Shell>
  );
}

function Baggage() {
  const [flightType, setFlightType] = useState("국제선");
  const [item, setItem] = useState("");
  const [amount, setAmount] = useState("");
  const [unit, setUnit] = useState("ml");
  const [result, setResult] = useState<Verdict | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  useEffect(() => { const query = new URLSearchParams(window.location.search).get("item"); if (query) check(query, true); }, []);
  const find = (value: string): Verdict => baggageData.view.verdicts.find((verdict) => verdict.match.some((match) => value.toLowerCase().includes(match.toLowerCase()))) ?? { ...baggageData.view.aiFallback, title: value };
  async function check(value = item, instant = false) {
    if (!value.trim()) return setError("수화물 품목을 입력해주세요.");
    setItem(value); setError(""); setLoading(true); if (!instant) await delay(500);
    const found = find(value); setResult(found.source === "ai" ? { ...found, title: [value, amount && `${amount}${unit}`].filter(Boolean).join(" ") } : found); setLoading(false);
  }
  const stateClass = (value: string) => `verdict ${value}`;
  return (
    <Shell route="/baggage">
      <section className="baggage-head"><div><p className="eyebrow">PACK OR LEAVE?</p><h1>{baggageData.page.prompt}</h1><p>제품명과 용량을 입력하면 기내·위탁 규정을 바로 구분해드려요.</p></div><div className="flight-toggle">{baggageData.view.flightTypes.map((value) => <button className={flightType === value ? "active" : ""} key={value} onClick={() => setFlightType(value)}>{value}</button>)}</div></section>
      <section className="baggage-search">
        <form onSubmit={(e) => { e.preventDefault(); check(); }}>
          <label><span>품목명</span><input value={item} onChange={(e) => setItem(e.target.value)} placeholder="예: 선크림, 보조배터리" /></label>
          <label className="amount"><span>용량</span><input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="150" /></label>
          <label className="unit"><span>단위</span><select value={unit} onChange={(e) => setUnit(e.target.value)}>{baggageData.view.units.map((value) => <option key={value}>{value}</option>)}</select></label>
          <button className="primary" disabled={loading}>{loading ? "확인 중…" : "규정 확인"}</button>
        </form>
        {error && <p className="field-error">{error}</p>}
        <div className="popular"><span>자주 찾는 품목</span><div>{baggageData.view.popularChips.map((value) => <button key={value} onClick={() => check(value)}>{value}</button>)}</div></div>
      </section>

      {loading && <div className="checker-loading"><span /><p>규정을 확인하고 있어요…</p></div>}
      {result && !loading && <section className="result-card">
        <header><div><p className="eyebrow">{flightType} · BAGGAGE RESULT</p><h2>{result.title}</h2></div><span className={result.source === "ai" ? "source ai" : "source"}>{result.source === "ai" ? "AI 판정" : "규칙 DB 판정"}</span></header>
        <div className="verdict-grid"><article className={stateClass(result.carryOn.verdict)}><span>기내 반입</span><strong>{result.carryOn.label}</strong><p>{result.carryOn.reason}</p></article><article className={stateClass(result.checked.verdict)}><span>위탁 수화물</span><strong>{result.checked.label}</strong><p>{result.checked.reason}</p></article></div>
        {result.tips && <div className="tip"><span>TIP</span><p>{result.tips}</p></div>}
        <footer><span>출처 · {result.reference}</span><button onClick={() => { setToast("목업: 오류 신고는 다음 단계에서 붙어요"); setTimeout(() => setToast(""), 2500); }}>오류 신고</button></footer>
      </section>}

      <section className="recent-search"><p className="eyebrow">RECENT CHECKS</p><h2>최근 확인</h2>{baggageData.view.recentSearches.map((value) => <button key={value} onClick={() => check(value)}><span>{value}</span><b>다시 확인 →</b></button>)}</section>
      <p className="legal-notice">ⓘ {baggageData.view.notice}</p>
      {toast && <Toast>{toast}</Toast>}
    </Shell>
  );
}

function Trips() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [trips, setTrips] = useState([...tripsData.view.trips]);
  const [menu, setMenu] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [renaming, setRenaming] = useState<string | null>(null);
  if (!loggedIn) return <Shell route="/trips" narrow><section className="logged-out"><span><Plane /></span><p className="eyebrow">YOUR TRIPS</p><h1>여행을 저장해두고<br />준비를 이어가세요.</h1><p>{tripsData.view.loginRequired}</p><button className="primary" onClick={() => { localStorage.setItem("tripkit-return", "/trips"); router.push("/login"); }}>로그인하기</button></section></Shell>;
  return (
    <Shell route="/trips" narrow>
      <section className="list-head"><div><p className="eyebrow">MY JOURNEYS</p><h1>내 여행</h1></div><button className="primary" onClick={() => router.push("/")}>+ 새 여행</button></section>
      {!trips.length ? <section className="empty"><Plane /><h2>{tripsData.view.emptyMessage}</h2><button className="primary" onClick={() => router.push("/")}>첫 리스트 만들기</button></section> : <div className="trip-cards">{trips.map((trip, index) => { const percent = Math.round(trip.progress.checked / trip.progress.total * 100); return <article key={trip.id} onClick={() => { sessionStorage.setItem("tripkit-title", trip.title); router.push("/trip"); }}>
        <span className="journey-code">T{String(index + 1).padStart(2, "0")}</span>
        <div className="journey-main">{renaming === trip.id ? <input autoFocus defaultValue={trip.title} onClick={(e) => e.stopPropagation()} onBlur={(e) => { setTrips(trips.map((value) => value.id === trip.id ? { ...value, title: e.target.value || value.title } : value)); setRenaming(null); }} /> : <h2>{trip.title}</h2>}<p>{trip.meta}</p><div className="journey-progress"><span><i style={{ width: `${percent}%` }} /></span><b>{trip.progress.checked}/{trip.progress.total}</b></div></div>
        <button className="more" onClick={(e) => { e.stopPropagation(); setMenu(menu === trip.id ? null : trip.id); }} aria-label="여행 메뉴">•••</button>
        {menu === trip.id && <div className="card-menu" onClick={(e) => e.stopPropagation()}><button onClick={() => { setRenaming(trip.id); setMenu(null); }}>이름 변경</button><button onClick={() => { setConfirm(trip.id); setMenu(null); }}>삭제</button></div>}
      </article>; })}</div>}
      {confirm && <div className="overlay"><section className="sheet confirm"><p className="eyebrow">DELETE TRIP</p><h2>이 여행을 삭제할까요?</h2><p>체크리스트와 메모가 함께 삭제됩니다.</p><div><button className="secondary" onClick={() => setConfirm(null)}>취소</button><button className="danger" onClick={() => { setTrips(trips.filter((trip) => trip.id !== confirm)); setConfirm(null); }}>삭제</button></div></section></div>}
    </Shell>
  );
}

function Login() {
  const router = useRouter();
  const [, setLoggedIn] = useAuth();
  const [tab, setTab] = useState("로그인");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const fields = tab === "로그인" ? authData.view.fields.login : authData.view.fields.signup;
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    if (tab === "회원가입" && String(form.get("비밀번호") || "").length < 8) return setError(authData.view.passwordRule);
    setError(""); setLoading(true); await delay(500); setLoggedIn(true);
    const target = localStorage.getItem("tripkit-return") || "/"; localStorage.removeItem("tripkit-return"); router.push(target);
  };
  return (
    <><Header route="/login" /><main className="auth-page"><section className="auth-poster"><div className="poster-route"><span>ICN</span><Plane /><span>ANY</span></div><div><p className="eyebrow">PACK LESS. GO FURTHER.</p><h1>준비는 가볍게,<br />여행은 더 멀리.</h1><p>한 번 만든 리스트를 저장하고 어디서든 이어서 준비하세요.</p></div><small>TRIPKIT · TRAVEL READY SERVICE</small></section><section className="auth-form"><div><p className="eyebrow">WELCOME TO TRIPKIT</p><h2>{tab === "로그인" ? "다시 만나 반가워요." : "여행 준비를 시작해요."}</h2><div className="tabs auth-tabs">{authData.view.tabs.map((value) => <button key={value} className={tab === value ? "active" : ""} onClick={() => { setTab(value); setError(""); }}>{value}</button>)}</div><form onSubmit={submit}>{fields.map((field) => <label key={field}>{field}<input name={field} type={field.includes("비밀번호") ? "password" : field === "이메일" ? "email" : "text"} placeholder={field === "이메일" ? "traveler@example.com" : field} /></label>)}{error && <p className="field-error">{error}</p>}<button className="primary" disabled={loading}>{loading ? "잠시만요…" : tab}</button></form>{tab === "로그인" && <button className="reset" onClick={() => { setToast("목업: 재설정 메일은 다음 단계에서 붙어요"); setTimeout(() => setToast(""), 2500); }}>비밀번호를 잊으셨나요?</button>}<p className="mock-note">실제 계정은 생성되지 않는 UI 목업입니다.</p></div></section>{toast && <Toast>{toast}</Toast>}</main></>
  );
}

export default function Mockup({ route }: { route: string }) {
  const page = useMemo(() => route.replace(/\/$/, "") || "/", [route]);
  if (page === "/") return <Home />;
  if (page === "/trip") return <Trip />;
  if (page === "/baggage") return <Baggage />;
  if (page === "/trips") return <Trips />;
  if (page === "/login") return <Login />;
  return <Shell route={page}><section className="empty"><h1>페이지를 찾을 수 없어요.</h1><a href="/">홈으로 돌아가기</a></section></Shell>;
}
