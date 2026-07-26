"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/api/auth";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";
import Toast from "@/components/Toast";
import * as api from "@/lib/api";

const copy = {
  loginRequired: "로그인하면 내 여행 리스트를 모두 볼 수 있어요.",
  emptyMessage: "아직 저장된 여행이 없어요.",
};

/**
 * 카드 부제목 생성.
 * 백엔드 TripResponse는 표시용 `meta` 문자열을 주지 않고 원본 값만 주므로
 * (duration_nights / departure_month) 프론트에서 조립한다.
 * app/trip/page.tsx와 동일한 규칙을 사용한다.
 */
function buildMeta(trip: api.Trip): string {
  const duration = trip.duration_nights
    ? `${trip.duration_nights}박 ${trip.duration_nights + 1}일`
    : "";
  const month = trip.departure_month ? `${trip.departure_month}월` : "";
  return [duration, month].filter(Boolean).join(" · ");
}

export default function Trips() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [trips, setTrips] = useState<api.Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [menu, setMenu] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [renaming, setRenaming] = useState<string | null>(null);

  const loadTrips = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getUserTrips(api.getAccessToken() || undefined);
      setTrips(data);
    } catch (err) {
      console.error("여행 목록 조회 실패:", err);
      setError("여행 목록을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!loggedIn) {
      setLoading(false);
      return;
    }
    loadTrips();
  }, [loggedIn, loadTrips]);

  /**
   * 여행 카드 진입.
   * trip 상세 페이지는 sessionStorage의 tripkit-trip-id를 기준으로 데이터를
   * 불러오므로, 반드시 id를 함께 심어야 한다. (title만 넣으면 직전 여행의
   * 데이터가 표시되는 버그가 생김)
   */
  const openTrip = (trip: api.Trip) => {
    sessionStorage.setItem("tripkit-trip-id", trip.id);
    sessionStorage.setItem("tripkit-title", trip.title);
    router.push("/trip");
  };

  const renameTrip = async (trip: api.Trip, nextTitle: string) => {
    const title = nextTitle.trim();
    setRenaming(null);
    if (!title || title === trip.title) return;

    // 낙관적 업데이트
    const previous = trips;
    setTrips((current) =>
      current.map((value) => (value.id === trip.id ? { ...value, title } : value))
    );

    try {
      // PATCH 응답에는 진행률이 집계되지 않으므로 title만 반영한다.
      const updated = await api.updateTripTitle(
        trip.id,
        title,
        api.getAccessToken() || undefined
      );
      setTrips((current) =>
        current.map((value) =>
          value.id === trip.id ? { ...value, title: updated.title } : value
        )
      );
    } catch (err) {
      console.error("이름 변경 실패:", err);
      setTrips(previous);
      setToast("이름 변경에 실패했습니다.");
    }
  };

  const removeTrip = async (tripId: string) => {
    setConfirm(null);
    const previous = trips;
    setTrips((current) => current.filter((trip) => trip.id !== tripId));

    try {
      await api.deleteTrip(tripId, api.getAccessToken() || undefined);
      setToast("여행을 삭제했어요");
    } catch (err) {
      console.error("여행 삭제 실패:", err);
      setTrips(previous);
      setToast("삭제에 실패했습니다.");
    }
  };

  if (!loggedIn) {
    return (
      <Shell route="/trips" narrow>
        <section className="logged-out">
          <p className="eyebrow">YOUR TRIPS</p>
          <h1>
            여행을 저장해두고<br />
            준비를 이어가세요.
          </h1>
          <p>{copy.loginRequired}</p>
          <button
            className="primary"
            onClick={() => {
              localStorage.setItem("tripkit-return", "/trips");
              router.push("/login");
            }}
          >
            로그인하기
          </button>
        </section>
      </Shell>
    );
  }

  if (loading) {
    return (
      <Shell route="/trips" narrow>
        <Loading />
      </Shell>
    );
  }

  return (
    <Shell route="/trips" narrow>
      <section className="list-head">
        <div>
          <p className="eyebrow">MY JOURNEYS</p>
          <h1>내 여행</h1>
        </div>
        <button className="primary" onClick={() => router.push("/")}>
          + 새 여행
        </button>
      </section>

      {error ? (
        <section className="empty">
          <h2>{error}</h2>
          <button className="primary" onClick={loadTrips}>
            다시 시도
          </button>
        </section>
      ) : !trips.length ? (
        <section className="empty">
          <h2>{copy.emptyMessage}</h2>
          <button className="primary" onClick={() => router.push("/")}>
            첫 리스트 만들기
          </button>
        </section>
      ) : (
        <div className="trip-cards">
          {trips.map((trip, index) => {
            const total = trip.items_count ?? 0;
            const checked = trip.checked_count ?? 0;
            // 아이템이 0개일 때 0으로 나누어 NaN이 되지 않도록 방어
            const percent = total > 0 ? Math.round((checked / total) * 100) : 0;

            return (
              <article key={trip.id} onClick={() => openTrip(trip)}>
                <span className="journey-code">
                  T{String(index + 1).padStart(2, "0")}
                </span>
                <div className="journey-main">
                  {renaming === trip.id ? (
                    <input
                      autoFocus
                      defaultValue={trip.title}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") e.currentTarget.blur();
                        if (e.key === "Escape") setRenaming(null);
                      }}
                      onBlur={(e) => renameTrip(trip, e.target.value)}
                    />
                  ) : (
                    <h2>{trip.title}</h2>
                  )}
                  <p>{buildMeta(trip)}</p>
                  <div className="journey-progress">
                    <span>
                      <i style={{ width: `${percent}%` }} />
                    </span>
                    <b>
                      {checked}/{total}
                    </b>
                  </div>
                </div>
                <button
                  className="more"
                  onClick={(e) => {
                    e.stopPropagation();
                    setMenu(menu === trip.id ? null : trip.id);
                  }}
                  aria-label="여행 메뉴"
                >
                  •••
                </button>
                {menu === trip.id && (
                  <div className="card-menu" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => {
                        setRenaming(trip.id);
                        setMenu(null);
                      }}
                    >
                      이름 변경
                    </button>
                    <button
                      onClick={() => {
                        setConfirm(trip.id);
                        setMenu(null);
                      }}
                    >
                      삭제
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}

      {confirm && (
        <div className="overlay" onClick={() => setConfirm(null)}>
          <section className="sheet confirm" onClick={(e) => e.stopPropagation()}>
            <p className="eyebrow">DELETE TRIP</p>
            <h2>이 여행을 삭제할까요?</h2>
            <p>체크리스트와 메모가 함께 삭제됩니다.</p>
            <div>
              <button className="secondary" onClick={() => setConfirm(null)}>
                취소
              </button>
              <button className="danger" onClick={() => removeTrip(confirm)}>
                삭제
              </button>
            </div>
          </section>
        </div>
      )}

      {toast && <Toast>{toast}</Toast>}
    </Shell>
  );
}
