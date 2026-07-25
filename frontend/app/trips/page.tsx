"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/api/auth";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";

const tripsData = {
  view: {
    trips: [
      { "id": "1", "title": "도쿄 여행", "meta": "4박 5일 · 3월", "progress": { "checked": 8, "total": 15 } },
      { "id": "2", "title": "제주 가족 여행", "meta": "3박 4일 · 6월", "progress": { "checked": 12, "total": 20 } }
    ],
    loginRequired: "로그인하면 내 여행 리스트를 모두 볼 수 있어요.",
    "emptyMessage": "아직 저장된 여행이 없어요."
  }
};

export default function Trips() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [trips, setTrips] = useState(tripsData.view.trips);
  const [menu, setMenu] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [renaming, setRenaming] = useState<string | null>(null);

  if (!loggedIn) {
    return (
      <Shell route="/trips" narrow>
        <section className="logged-out">
          <Loading />
          <p className="eyebrow">YOUR TRIPS</p>
          <h1>
            여행을 저장해두고<br />
            준비를 이어가세요.
          </h1>
          <p>{tripsData.view.loginRequired}</p>
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

      {!trips.length ? (
        <section className="empty">
          <Loading />
          <h2>{tripsData.view.emptyMessage}</h2>
          <button className="primary" onClick={() => router.push("/")}>
            첫 리스트 만들기
          </button>
        </section>
      ) : (
        <div className="trip-cards">
          {trips.map((trip, index) => {
            const percent = Math.round((trip.progress.checked / trip.progress.total) * 100);
            return (
              <article
                key={trip.id}
                onClick={() => {
                  sessionStorage.setItem("tripkit-title", trip.title);
                  router.push("/trip");
                }}
              >
                <span className="journey-code">
                  T{String(index + 1).padStart(2, "0")}
                </span>
                <div className="journey-main">
                  {renaming === trip.id ? (
                    <input
                      autoFocus
                      defaultValue={trip.title}
                      onClick={(e) => e.stopPropagation()}
                      onBlur={(e) => {
                        setTrips(
                          trips.map((value) =>
                            value.id === trip.id ? { ...value, title: e.target.value || value.title } : value
                          )
                        );
                        setRenaming(null);
                      }}
                    />
                  ) : (
                    <h2>{trip.title}</h2>
                  )}
                  <p>{trip.meta}</p>
                  <div className="journey-progress">
                    <span>
                      <i style={{ width: `${percent}%` }} />
                    </span>
                    <b>
                      {trip.progress.checked}/{trip.progress.total}
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
                  <div
                    className="card-menu"
                    onClick={(e) => e.stopPropagation()}
                  >
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
        <div className="overlay">
          <section className="sheet confirm">
            <p className="eyebrow">DELETE TRIP</p>
            <h2>이 여행을 삭제할까요?</h2>
            <p>체크리스트와 메모가 함께 삭제됩니다.</p>
            <div>
              <button
                className="secondary"
                onClick={() => setConfirm(null)}
              >
                취소
              </button>
              <button
                className="danger"
                onClick={() => {
                  setTrips(trips.filter((trip) => trip.id !== confirm));
                  setConfirm(null);
                }}
              >
                삭제
              </button>
            </div>
          </section>
        </div>
      )}
    </Shell>
  );
}