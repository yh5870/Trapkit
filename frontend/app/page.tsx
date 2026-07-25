"use client";

import { FormEvent, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";
import Toast from "@/components/Toast";
import Plane from "@/components/Plane";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/api/auth";

export default function Home() {
  const router = useRouter();
  const [loggedIn] = useAuth();
  const [destination, setDestination] = useState("");
  useEffect(() => {
    console.log("token:", api.getAccessToken());
    console.log("isAuthenticated:", api.isAuthenticated());
    console.log("loggedIn:", loggedIn);
  }, [loggedIn]);
  const [purposes, setPurposes] = useState<string[]>([]);
  const [optional, setOptional] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [customPurpose, setCustomPurpose] = useState("");
  const [toast, setToast] = useState<string | null>(null);

  const homeData = {
    page: {
      tagline: "당신의 여행에 딱 맞는 패킹 리스트를 만들어드려요.",
      prompt: "어디로 여행을 가시나요?"
    },
    view: {
      placeholders: {
        destination: "예: 도쿄, 파리, 제주도"
      },
      purposeChips: ["일본 여행", "출장", "가족 여행", "캠핑"],
      optionalFields: {
        durationLabel: "여행 기간",
        monthLabel: "출발 시기"
      },
      baggageShortcut: {
        title: "수화물 체커",
        subtitle: "기내·위탁 규정 바로 확인",
        popularChips: ["선크림", "보조배터리", "액체류"]
      },
      recentTrips: [
        { id: "1", title: "도쿄 여행", meta: "3박 4일 · 12월 25일 출발" },
        { id: "2", title: "제주도 가족 여행", meta: "2박 3일 · 11월 10일 출발" }
      ]
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!destination.trim()) return setError("목적지를 입력해 주세요.");
    setError(""); setLoading(true);
    sessionStorage.setItem("tripkit-destination", destination.trim());
    try {
      const finalPurposes = purposes.length > 0 ? purposes : (customPurpose.trim() ? [customPurpose.trim()] : ["관광"]);

      await api.generateTripWithStream(
        {
          destination: destination.trim(),
          purpose: finalPurposes
        },
        api.getAccessToken() || undefined,
        (message) => {
          console.log('SSE Message:', message);
        },
        (trip) => {
          sessionStorage.setItem("tripkit-trip-id", trip.id);
          sessionStorage.setItem("tripkit-title", trip.title);
          router.push("/trip");
        },
        (error) => {
          setError(error);
          setLoading(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "여행 리스트 생성에 실패했습니다.");
      setLoading(false);
    }
  };

  const baggage = (item?: string) => router.push(`/baggage${item ? `?item=${encodeURIComponent(item)}` : ""}`);

  if (loading) return <Shell route="/"><Loading /></Shell>;

  return (
    <Shell route="/">
      <section className="home-hero">
        <div className="hero-copy">
          <p className="eyebrow">YOUR TRIP, PACKED RIGHT</p>
          <h1>가방을 열기 전에,<br /><em>여행을 먼저 담아요.</em></h1>
          <p>{homeData.page.tagline}. 블로그를 뒤지는 대신 이번 여행에 맞는 준비를 바로 시작하세요.</p>
        </div>
        <div className="route-stamp" aria-hidden="true">
          <span>ICN</span><i><Plane className="flying-plane" /></i><span>CTS</span>
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
              placeholder={homeData.view.placeholders.destination}
            />
            <span className="airport-code">DESTINATION</span>
          </div>
          {error && <p className="field-error">{error}</p>}

          <fieldset>
            <legend>어떤 여행인가요?</legend>
            <div className="chips">
              {homeData.view.purposeChips.map((purpose) => (
                <button
                  type="button"
                  key={purpose}
                  className={purposes.includes(purpose) ? "selected" : ""}
                  onClick={() => setPurposes((current) => current.includes(purpose) ? current.filter((item) => item !== purpose) : [...current, purpose])}
                >
                  {purpose}
                </button>
              ))}
              <input
                aria-label="여행 목적 직접 입력"
                placeholder="직접 입력 +"
                value={customPurpose}
                onChange={(e) => setCustomPurpose(e.target.value)}
              />
            </div>
            {!purposes.length && !customPurpose && <p className="helper">선택하지 않으면 일반 관광 기준으로 만들어요.</p>}
          </fieldset>

          <button
            type="button"
            className="optional-toggle"
            onClick={() => setOptional(!optional)}
            aria-expanded={optional}
          >
            <span>{optional ? "−" : "+"}</span> 기간 · 출발 시기 · 동행 입력 <small>선택</small>
          </button>
          {optional && (
            <div className="optional-grid">
              <label>{homeData.view.optionalFields.durationLabel}
                <select defaultValue="4박 5일">
                  <option>2박 3일</option>
                  <option>3박 4일</option>
                  <option>4박 5일</option>
                  <option>직접 입력</option>
                </select>
              </label>
              <label>{homeData.view.optionalFields.monthLabel}
                <input type="month" defaultValue="2026-12" />
              </label>
              <label>동행
                <select defaultValue="친구">
                  <option>혼자</option>
                  <option>커플</option>
                  <option>친구</option>
                  <option>가족·유아 동반</option>
                </select>
              </label>
            </div>
          )}
          <button className="primary cta" type="submit">
            <span>내 여행 리스트 만들기</span><span aria-hidden="true">→</span>
          </button>
        </div>
      </form>

      <section className="home-grid">
        {loggedIn && (
          <div className="recent-section">
            <div className="section-heading">
              <p className="eyebrow">CONTINUE PACKING</p>
              <h2>최근 여행</h2>
            </div>
            <div className="recent-list">
              {homeData.view.recentTrips.map((trip, index) => (
                <button key={trip.id} onClick={() => router.push("/trip")}>
                  <span className="trip-number">0{index + 1}</span>
                  <span>
                    <strong>{trip.title}</strong>
                    <small>{trip.meta}</small>
                  </span>
                  <b>→</b>
                </button>
              ))}
            </div>
          </div>
        )}
        <button className="baggage-shortcut" onClick={() => baggage()}>
          <span className="luggage-handle"></span>
          <span className="eyebrow">BAGGAGE QUICK CHECK</span>
          <strong>{homeData.view.baggageShortcut.title}</strong>
          <span>{homeData.view.baggageShortcut.subtitle} <b>→</b></span>
          <span className="mini-chips">
            {homeData.view.baggageShortcut.popularChips.slice(0, 3).map((chip) => (
              <i
                key={chip}
                onClick={(e) => {
                  e.stopPropagation();
                  baggage(chip);
                }}
              >
                {chip}
              </i>
            ))}
          </span>
        </button>
      </section>
      {toast && <Toast>{toast}</Toast>}
    </Shell>
  );
}