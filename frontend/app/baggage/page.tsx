"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";
import Toast from "@/components/Toast";
import * as api from "@/lib/api";

type Verdict = {
  source: string;
  title: string;
  match: string[];
  carryOn: { verdict: string; label: string; reason: string };
  checked: { verdict: string; label: string; reason: string };
  tips?: string;
  reference: string;
};

export default function Baggage() {
  const [flightType, setFlightType] = useState("국제선");
  const [item, setItem] = useState("");
  const [amount, setAmount] = useState("");
  const [unit, setUnit] = useState("ml");
  const [result, setResult] = useState<Verdict | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const baggageData = {
    page: {
      prompt: "가져가실 품목의 규정을 확인해보세요."
    },
    view: {
      flightTypes: ["국제선", "국내선"],
      units: ["ml", "g", "개", "L"],
      verdicts: [
        {
          match: ["선크림", "로션"],
          title: "선크림/로션",
          source: "db",
          carryOn: { verdict: "caution", label: "제한 있음", reason: "100ml 이하만 기내 반입 가능" },
          checked: { verdict: "allowed", label: "가능", reason: "용량 제한 없이 위탁 가능" },
          tips: "용량 표시가 있는 용기에 담아주세요.",
          reference: "공항 규정"
        },
        {
          match: ["보조배터리"],
          title: "보조배터리",
          source: "db",
          carryOn: { verdict: "caution", label: "제한 있음", reason: "100Wh 이하만 기내 반입 가능" },
          checked: { verdict: "prohibited", label: "불가", reason: "보조배터리는 위탁 반입 금지" },
          tips: "백분율 용량 표시를 확인해주세요.",
          reference: "항공안전 규정"
        }
      ],
      popularChips: ["선크림", "보조배터리", "액체류", "무선 이어폰"],
      recentSearches: ["선크림", "보조배터리", "헤어스프레이"],
      notice: "각 항공사 규정이 다를 수 있습니다. 출발 전 반드시 확인해주세요.",
      aiFallback: {
        source: "ai",
        title: "알 수 없음",
        carryOn: { verdict: "unknown", label: "확인 필요", reason: "정보가 부족하여 판정할 수 없습니다." },
        checked: { verdict: "unknown", label: "확인 필요", reason: "정보가 부족하여 판정할 수 없습니다." },
        tips: "항공사에 문의하거나 기내 반입 규정을 확인해주세요.",
        reference: "AI 분석 결과"
      }
    }
  };

  useEffect(() => {
    const query = new URLSearchParams(window.location.search).get("item");
    if (query) check(query, true);
  }, []);

  const find = (value: string): Verdict =>
    baggageData.view.verdicts.find((verdict) =>
      verdict.match.some((match) => value.toLowerCase().includes(match.toLowerCase()))
    ) ?? { ...baggageData.view.aiFallback, title: value, match: [value] };

  async function check(value = item, instant = false) {
    if (!value.trim()) return setError("수화물 품목을 입력해주세요.");

    setItem(value);
    setError("");
    setLoading(true);
    if (!instant) await new Promise((resolve) => setTimeout(resolve, 500));

    try {
      const amountValue = parseFloat(amount) || 0;
      const unitMapping: Record<string, "ml" | "g" | "l" | "kg" | "inch" | "cm"> = {
        "ml": "ml",
        "g": "g",
        "개": "g",
        "L": "l",
        "kg": "kg",
        "inch": "inch",
        "cm": "cm"
      };
      const apiUnit = unitMapping[unit] || "g";

      const response = await api.checkBaggage(
        {
          airline: flightType === "국제선" ? "대한항공" : "제주항공",
          product: value,
          value: amountValue,
          unit: apiUnit
        },
        api.getAccessToken() || undefined
      );

      setResult({
        source: "db",
        title: value,
        match: [value],
        carryOn: {
          verdict: response.carry_on.verdict,
          label: response.carry_on.label,
          reason: response.carry_on.reason
        },
        checked: {
          verdict: response.checked.verdict,
          label: response.checked.label,
          reason: response.checked.reason
        },
        tips: "항공사 규정에 따라 다를 수 있습니다.",
        reference: "규칙 DB 판정"
      });
    } catch (err) {
      const fallback = find(value);
      setResult(
        fallback.source === "ai"
          ? { ...fallback, title: [value, amount && `${amount}${unit}`].filter(Boolean).join(" ") }
          : fallback
      );
    }

    setLoading(false);
  }

  const stateClass = (value: string) => `verdict ${value}`;

  return (
    <Shell route="/baggage">
      <section className="baggage-head">
        <div>
          <p className="eyebrow">PACK OR LEAVE?</p>
          <h1>{baggageData.page.prompt}</h1>
          <p>제품명과 용량을 입력하면 기내·위탁 규정을 바로 구분해드려요.</p>
        </div>
        <div className="flight-toggle">
          {baggageData.view.flightTypes.map((value) => (
            <button
              key={value}
              className={flightType === value ? "active" : ""}
              onClick={() => setFlightType(value)}
            >
              {value}
            </button>
          ))}
        </div>
      </section>

      <section className="baggage-search">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            check();
          }}
        >
          <label>
            <span>품목명</span>
            <input
              value={item}
              onChange={(e) => setItem(e.target.value)}
              placeholder="예: 선크림, 보조배터리"
            />
          </label>
          <label className="amount">
            <span>용량</span>
            <input
              inputMode="numeric"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="150"
            />
          </label>
          <label className="unit">
            <span>단위</span>
            <select value={unit} onChange={(e) => setUnit(e.target.value)}>
              {baggageData.view.units.map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>
          <button className="primary" disabled={loading}>
            {loading ? "확인 중…" : "규정 확인"}
          </button>
        </form>
        {error && <p className="field-error">{error}</p>}
        <div className="popular">
          <span>자주 찾는 품목</span>
          <div>
            {baggageData.view.popularChips.map((value) => (
              <button key={value} onClick={() => check(value)}>{value}</button>
            ))}
          </div>
        </div>
      </section>

      {loading && (
        <div className="checker-loading">
          <span />
          <p>규정을 확인하고 있어요…</p>
        </div>
      )}
      {result && !loading && (
        <section className="result-card">
          <header>
            <div>
              <p className="eyebrow">
                {flightType} · BAGGAGE RESULT
              </p>
              <h2>{result.title}</h2>
            </div>
            <span className={result.source === "ai" ? "source ai" : "source"}>
              {result.source === "ai" ? "AI 판정" : "규칙 DB 판정"}
            </span>
          </header>
          <div className="verdict-grid">
            <article className={stateClass(result.carryOn.verdict)}>
              <span>기내 반입</span>
              <strong>{result.carryOn.label}</strong>
              <p>{result.carryOn.reason}</p>
            </article>
            <article className={stateClass(result.checked.verdict)}>
              <span>위탁 수화물</span>
              <strong>{result.checked.label}</strong>
              <p>{result.checked.reason}</p>
            </article>
          </div>
          {result.tips && (
            <div className="tip">
              <span>TIP</span>
              <p>{result.tips}</p>
            </div>
          )}
          <footer>
            <span>출처 · {result.reference}</span>
            <button
              onClick={() => {
                setToast("목업: 오류 신고는 다음 단계에서 붙어요");
                setTimeout(() => setToast(""), 2500);
              }}
            >
              오류 신고
            </button>
          </footer>
        </section>
      )}

      <section className="recent-search">
        <p className="eyebrow">RECENT CHECKS</p>
        <h2>최근 확인</h2>
        {baggageData.view.recentSearches.map((value) => (
          <button key={value} onClick={() => check(value)}>
            <span>{value}</span>
            <b>다시 확인 →</b>
          </button>
        ))}
      </section>
      <p className="legal-notice">ⓘ {baggageData.view.notice}</p>
      {toast && <Toast>{toast}</Toast>}
    </Shell>
  );
}