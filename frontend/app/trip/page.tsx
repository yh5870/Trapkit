"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";
import Toast from "@/components/Toast";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/api/auth";
import tripData from "@/data/trip.json";

type TripItem = {
  id: string;
  name: string;
  quantity: string | null;
  tip: string | null;
  baggageFlag: api.BaggageFlag | null;
  source: "ai" | "user";
  checked: boolean;
  category?: string;
};

type Category = {
  name: string;
  items: TripItem[];
};

type Caution = api.Caution;

type BaggageAlert = api.BaggageSummaryEntry;

const BAGGAGE_FLAG_LABEL: Record<api.BaggageFlag, string> = {
  carry_on_only: "기내만",
  checked_only: "위탁만",
  restricted: "제한 있음",
};

/**
 * baggage_flag를 안전하게 정규화한다.
 * 과거 데이터에 문자열 "True"/"False"가 저장된 적이 있어,
 * 알 수 없는 값은 null로 떨어뜨려 배지를 숨긴다.
 */
function normalizeBaggageFlag(raw: unknown): api.BaggageFlag | null {
  if (typeof raw !== "string") return null;
  const value = raw.toLowerCase();
  // `in` 대신 hasOwnProperty로 프로토타입 체인("constructor" 등) 오탐을 차단
  return Object.prototype.hasOwnProperty.call(BAGGAGE_FLAG_LABEL, value)
    ? (value as api.BaggageFlag)
    : null;
}

// 아이템을 카테고리별로 정리하는 함수
function organizeItemsByCategory(items: api.TripItem[]): Category[] {
  const grouped = new Map<string, TripItem[]>();

  items.forEach((item) => {
    const category = item.category || "기타";
    if (!grouped.has(category)) {
      grouped.set(category, []);
    }
    grouped.get(category)!.push({
      id: item.id,
      name: item.name,
      quantity: item.quantity,
      tip: item.tip,
      baggageFlag: normalizeBaggageFlag(item.baggage_flag),
      source: item.source,
      checked: item.checked,
      category: item.category,
    });
  });

  return Array.from(grouped.entries()).map(([name, items]) => ({
    name,
    items,
  }));
}

export default function Trip() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [tab, setTab] = useState("체크리스트");
  const [title, setTitle] = useState("");
  const [meta, setMeta] = useState("");
  const [editingTitle, setEditingTitle] = useState(false);
  const [adding, setAdding] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [deleted, setDeleted] = useState<{ category: number; item: TripItem } | null>(null);
  const [sheet, setSheet] = useState<"login" | "regenerate" | null>(null);
  const [loading, setLoading] = useState(true);
  const [memo, setMemo] = useState("");
  const [memos, setMemos] = useState<api.Memo[]>([]);
  const [regenerateMode, setRegenerateMode] = useState("keep");
  const [cautions, setCautions] = useState<Caution[]>([]);
  const [baggageSummary, setBaggageSummary] = useState<BaggageAlert[]>([]);
  const [cautionNotice, setCautionNotice] = useState("");
  const [tripId, setTripId] = useState<string | null>(null);

  const total = categories.reduce((sum, category) => sum + category.items.length, 0);
  const checked = categories.reduce((sum, category) => sum + category.items.filter((item) => item.checked).length, 0);
  const percent = Math.round((checked / Math.max(total, 1)) * 100);

  // 여행 데이터 로드
  useEffect(() => {
    const loadTripData = async () => {
      const storedTripId = sessionStorage.getItem("tripkit-trip-id");
      const storedTitle = sessionStorage.getItem("tripkit-title");

      if (!storedTripId) {
        setLoading(false);
        return;
      }

      // 여행 조회 API는 인증이 필수다. 토큰 없이 호출하면 백엔드가
      // 401 "Authorization header missing"을 던지고 화면이 에러로 끝나므로,
      // 미리 로그인으로 유도한다. (복귀 후 이 페이지로 되돌아옴)
      if (!api.getAccessToken()) {
        localStorage.setItem("tripkit-return", "/trip");
        router.push("/login");
        return;
      }

      try {
        setTripId(storedTripId);

        // Trip 정보 가져오기 
        const trip = await api.getTripById(storedTripId, api.getAccessToken() || undefined);
        setTitle(storedTitle || trip.title);

        if (!trip) return;

        // 메타 정보 생성
        const duration = trip.duration_nights ? `${trip.duration_nights}박 ${trip.duration_nights + 1}일` : "";
        const month = trip.departure_month ? `${trip.departure_month}월` : "";
        const date = trip.created_at ? new Date(trip.created_at).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) : "";
        setMeta([duration, month, date].filter(Boolean).join(" · "));

        // 아이템 목록 가져오기
        const items = await api.getTripItems(storedTripId, api.getAccessToken() || undefined);
        setCategories(organizeItemsByCategory(items));

        // 메모 가져오기
        const tripMemos = await api.getMemosByTripId(storedTripId, api.getAccessToken() || undefined);
        setMemos(tripMemos);

        // 주의사항 및 수화물 요약 설정
        if (trip.cautions && trip.cautions.length > 0) {
          setCautions(trip.cautions);
        }

        if (trip.baggage_summary && trip.baggage_summary.length > 0) {
          setBaggageSummary(trip.baggage_summary);
        }

        setCautionNotice("출발 전 공항 규정을 다시 확인해주세요.");
      } catch (err) {
        console.error("여행 데이터 로드 실패:", err);
        setToast("여행 데이터를 불러오는데 실패했습니다.");
      } finally {
        setLoading(false);
      }
    };

    loadTripData();
  }, [router]);

  const toggle = (id: string) => setCategories((current) =>
    current.map((category) => ({
      ...category,
      items: category.items.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      ),
    }))
  );

  const add = (categoryName: string, name: string) => {
    if (!name.trim()) return;
    setCategories((current) =>
      current.map((category) =>
        category.name === categoryName
          ? {
              ...category,
              items: [
                ...category.items,
                {
                  id: `user-${Date.now()}`,
                  name: name.trim(),
                  quantity: null,
                  tip: null,
                  baggageFlag: null,
                  source: "user" as const,
                  checked: false,
                } as TripItem,
              ],
            }
          : category
      )
    );
    setAdding(null);
  };

  const remove = (categoryIndex: number, item: TripItem) => {
    setCategories((current) =>
      current.map((category, index) =>
        index === categoryIndex
          ? { ...category, items: category.items.filter((value) => value.id !== item.id) }
          : category
      )
    );
    setDeleted({ category: categoryIndex, item });
    setToast("항목을 삭제했어요");
  };

  const undo = () => {
    if (!deleted) return;
    setCategories((current) =>
      current.map((category, index) =>
        index === deleted.category
          ? { ...category, items: [...category.items, deleted.item] }
          : category
      )
    );
    setDeleted(null);
    setToast(null);
  };

  const regenerate = async () => {
    const userItems = categories
      .flatMap((category) =>
        category.items.filter((item) => item.source === "user").map((item) => ({ category: category.name, item }))
      );
    setSheet(null);
    setLoading(true);

    try {
      if (tripId) {
        // 실제 API를 사용하여 새로운 리스트 생성
        const newItems = await api.getTripItems(tripId, api.getAccessToken() || undefined);
        const fresh = organizeItemsByCategory(newItems);

        if (regenerateMode === "keep") {
          userItems.forEach(({ category, item }) => {
            const target = fresh.find((value) => value.name === category);
            if (target && !target.items.some((value) => value.id === item.id)) {
              target.items.push(item);
            }
          });
        }
        setCategories(fresh);
      } else {
        // tripId가 없으면 정적 데이터 사용
        const fresh = structuredClone(tripData.view.categories) as Category[];
        if (regenerateMode === "keep") {
          userItems.forEach(({ category, item }) => {
            const target = fresh.find((value) => value.name === category);
            if (target && !target.items.some((value) => value.id === item.id)) {
              target.items.push(item);
            }
          });
        }
        setCategories(fresh);
      }
    } catch (err) {
      console.error("리스트 재생성 실패:", err);
      setToast("리스트 재생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const save = () => (loggedIn ? setToast("저장됨") : setSheet("login"));

  const addMemo = async () => {
    if (!memo.trim()) return;
    try {
      const tripId = sessionStorage.getItem("tripkit-trip-id") || "mock-trip-id";
      const newMemo = await api.createMemo(tripId, memo.trim(), api.getAccessToken() || undefined);
      setMemos([newMemo, ...memos]);
      setMemo("");
      setTimeout(() => setToast("저장됨"), 1000);
    } catch (err) {
      setToast("메모 저장에 실패했습니다.");
    }
  };

  if (loading) return <Shell route="/trip"><Loading /></Shell>;

  return (
    <Shell route="/trip">
      <section className="trip-head">
        <p className="eyebrow">PACKING LIST · CTS</p>
        <div className="trip-title-row">
          <div>
            {editingTitle ? (
              <input
                autoFocus
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                onBlur={() => setEditingTitle(false)}
                onKeyDown={(e) => e.key === "Enter" && setEditingTitle(false)}
              />
            ) : (
              <h1 onClick={() => setEditingTitle(true)}>
                {title} <small>✎</small>
              </h1>
            )}
            <p>{meta}</p>
          </div>
          <div className="progress-copy">
            <strong>
              {checked}<span>/{total}</span>
            </strong>
            <small>{percent}% 준비 완료</small>
          </div>
        </div>
        <div className="progress-track">
          <span style={{ width: `${percent}%` }} />
        </div>
      </section>

      <div className="tabs" role="tablist">
        {["체크리스트", "주의사항", "메모"].map((value) => (
          <button
            role="tab"
            aria-selected={tab === value}
            className={tab === value ? "active" : ""}
            key={value}
            onClick={() => setTab(value)}
          >
            {value}
            {value === "체크리스트" && <span>{total}</span>}
          </button>
        ))}
      </div>

      {tab === "체크리스트" && (
        <div className="trip-layout">
          <section className="checklist">
            {categories.map((category, categoryIndex) => {
              const count = category.items.filter((item) => item.checked).length;
              return (
                <details className="category" key={category.name} open={categoryIndex < 2}>
                  <summary>
                    <span>{category.name}</span>
                    <small>
                      {count}/{category.items.length}
                    </small>
                    <i>⌄</i>
                  </summary>
                  <div className="items">
                    {category.items.map((item) => (
                      <div
                        className={`check-item ${item.checked ? "done" : ""}`}
                        key={item.id}
                      >
                        <button
                          className="checkbox"
                          onClick={() => toggle(item.id)}
                          aria-label={`${item.name} ${item.checked ? "체크 해제" : "체크"}`}
                        >
                          {item.checked && "✓"}
                        </button>
                        <div className="item-copy">
                          <div>
                            <strong>{item.name}</strong>
                            {item.quantity && <span>{item.quantity}</span>}
                            {item.source === "user" && <em>내가 추가</em>}
                          </div>
                          {item.tip && <small>{item.tip}</small>}
                        </div>
                        {item.baggageFlag && (
                          <button
                            className="baggage-badge"
                            onClick={() =>
                              router.push(`/baggage?item=${encodeURIComponent(item.name)}`)
                            }
                          >
                            ⚠ {BAGGAGE_FLAG_LABEL[item.baggageFlag]}
                          </button>
                        )}
                        <button
                          className="delete-item"
                          onClick={() => remove(categoryIndex, item)}
                          aria-label={`${item.name} 삭제`}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                  {adding === category.name ? (
                    <form
                      className="add-item"
                      onSubmit={(e) => {
                        e.preventDefault();
                        add(category.name, new FormData(e.currentTarget).get("item") as string);
                      }}
                    >
                      <input name="item" autoFocus placeholder="준비물 이름" />
                      <button>추가</button>
                      <button type="button" onClick={() => setAdding(null)}>
                        취소
                      </button>
                    </form>
                  ) : (
                    <button className="add-link" onClick={() => setAdding(category.name)}>
                      + 항목 추가
                    </button>
                  )}
                </details>
              );
            })}
          </section>
          <aside className="baggage-summary">
            <span className="summary-icon">!</span>
            <p className="eyebrow">BAGGAGE ALERT</p>
            <h2>
              확인할 수화물<br />규정이 {baggageSummary.length}건 있어요
            </h2>
            {baggageSummary.map((item) => (
              <button
                key={item.category}
                onClick={() => router.push(`/baggage?item=${encodeURIComponent(item.category)}`)}
              >
                <strong>{item.category}</strong>
                <span>{item.count}</span>
                <b>→</b>
              </button>
            ))}
          </aside>
        </div>
      )}

      {tab === "주의사항" && (
        <section className="caution-grid">
          {cautions.map((caution, index) => (
            // 💡 index를 결합하여 키 중복(undefined-undefined)을 원천 차단합니다.
            <article key={`caution-${index}`}>
              <div>
                {/* API 데이터 구조에 맞춰 안전하게 출력 */}
                <span>{caution.category || "주의사항"}</span>
                {/* confidence가 check_required면 재확인이 필요한 정보임을 표시 */}
                <em>{caution.confidence === "check_required" ? "확인 필요" : "출발 전 확인"}</em>
              </div>
              <p>{caution.text || "내용이 없습니다."}</p>
            </article>
          ))}
          <div className="notice">
            <strong>꼭 확인하세요</strong>
            <p>{cautionNotice}</p>
          </div>
        </section>
      )}

      {tab === "메모" && (
        <section className="memo-layout">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              addMemo();
            }}
          >
            <label htmlFor="memo">여행 전에 기억할 것</label>
            <textarea
              id="memo"
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="예약 번호, 이동 방법, 꼭 가볼 곳을 적어두세요."
            />
            <button className="primary">메모 추가</button>
          </form>
          <div className="memo-list">
            {memos.map((memoItem) => (
              <article key={memoItem.id}>
                <p>{memoItem.content}</p>
                <small>{new Date(memoItem.updated_at).toLocaleDateString('ko-KR')}</small>
                <button
                  onClick={async () => {
                    try {
                      await api.deleteMemo(memoItem.id, api.getAccessToken() || undefined);
                      setMemos(memos.filter((m) => m.id !== memoItem.id));
                      setToast("메모가 삭제되었습니다.");
                    } catch (err) {
                      setToast("메모 삭제에 실패했습니다.");
                    }
                  }}
                >
                  삭제
                </button>
              </article>
            ))}
          </div>
        </section>
      )}

      <div className="trip-actions">
        <button className="secondary" onClick={() => setSheet("regenerate")}>
          ↻ 다시 생성
        </button>
        <button className="primary" onClick={save}>
          리스트 저장
        </button>
      </div>
      {toast && <Toast action={deleted ? undo : undefined}>{toast}</Toast>}
      {sheet && (
        <div className="overlay" onClick={() => setSheet(null)}>
          <section className="sheet" onClick={(e) => e.stopPropagation()}>
            <span className="sheet-handle" />
            {sheet === "login" ? (
              <>
                <p className="eyebrow">SAVE YOUR TRIP</p>
                <h2>
                  리스트를 저장하려면<br />로그인이 필요합니다.
                </h2>
                <p>지금 만든 리스트는 로그인 후 그대로 저장돼요.</p>
                <button
                  className="primary"
                  onClick={() => {
                    localStorage.setItem("tripkit-return", "/trip");
                    router.push("/login");
                  }}
                >
                  로그인하기
                </button>
              </>
            ) : (
              <>
                <p className="eyebrow">REBUILD LIST</p>
                <h2>어떻게 다시 만들까요?</h2>
                <label>
                  <input
                    type="radio"
                    name="regenerate"
                    checked={regenerateMode === "keep"}
                    onChange={() => setRegenerateMode("keep")}
                  />
                  <span>
                    <strong>내 항목은 유지하기</strong>
                    <small>내가 추가한 항목을 빼고 새로 받아요.</small>
                  </span>
                </label>
                <label>
                  <input
                    type="radio"
                    name="regenerate"
                    checked={regenerateMode === "all"}
                    onChange={() => setRegenerateMode("all")}
                  />
                  <span>
                    <strong>전체 새로 받기</strong>
                    <small>모든 항목을 처음부터 다시 만들어요.</small>
                  </span>
                </label>
                <button className="primary" onClick={regenerate}>
                  다시 만들기
                </button>
              </>
            )}
          </section>
        </div>
      )}
    </Shell>
  );
}