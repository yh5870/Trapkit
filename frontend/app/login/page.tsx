"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import Loading from "@/components/Loading";
import Toast from "@/components/Toast";
import Plane from "@/components/Plane";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/api/auth";

export default function Login() {
  const router = useRouter();
  const [, setLoggedIn] = useAuth();
  const [tab, setTab] = useState("로그인");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const authData = {
    view: {
      tabs: ["로그인", "회원가입"],
      fields: {
        login: ["이메일", "비밀번호"],
        signup: ["이름", "이메일", "비밀번호"]
      },
      passwordRule: "비밀번호는 영문과 숫자를 포함해 8자 이상이어야 합니다."
    }
  };

  const fields = tab === "로그인" ? authData.view.fields.login : authData.view.fields.signup;

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    if (tab === "회원가입") {
      // 백엔드 SignupRequest.validate_password 와 동일한 규칙.
      // 길이만 검사하면 영문/숫자 조건에서 422가 나고, 그 에러가
      // 사용자에게 원인 없이 표시된다.
      const password = String(form.get("비밀번호") || "");
      const valid =
        password.length >= 8 &&
        /[A-Za-z]/.test(password) &&
        /[0-9]/.test(password);
      if (!valid) return setError(authData.view.passwordRule);
    }

    setError("");
    setLoading(true);

    try {
      if (tab === "로그인") {
        const response = await api.login({
          email: String(form.get("이메일")),
          password: String(form.get("비밀번호"))
        });
        api.setAccessToken(response.access_token);
        api.setUserId(response.user.id);
        setLoggedIn(true);
      } else {
        // /signup 은 토큰을 반환하지 않으므로 가입 직후 로그인까지 수행한다.
        const response = await api.signupAndLogin({
          nickname: String(form.get("이름")),
          email: String(form.get("이메일")),
          password: String(form.get("비밀번호"))
        });
        api.setAccessToken(response.access_token);
        api.setUserId(response.user.id);
        setLoggedIn(true);
      }

      const target = localStorage.getItem("tripkit-return") || "/";
      localStorage.removeItem("tripkit-return");
      router.push(target);
    } catch (err) {
      setError(err instanceof Error ? err.message : "인증에 실패했습니다.");
      setLoading(false);
    }
  };

  return (
    <>
      <Shell route="/login" narrow>
        <section className="auth-poster">
          <div className="poster-route">
            <span>ICN</span>
            <Plane className="flying-plane" />
            <span>ANY</span>
          </div>
          <div>
            <p className="eyebrow">PACK LESS. GO FURTHER.</p>
            <h1>
              준비는 가볍게,<br />
              여행은 더 멀리.
            </h1>
            <p>한 번 만든 리스트를 저장하고 어디서든 이어서 준비하세요.</p>
          </div>
          <small>TRIPKIT · TRAVEL READY SERVICE</small>
        </section>

        <section className="auth-form">
          <div>
            <p className="eyebrow">WELCOME TO TRIPKIT</p>
            <h2>
              {tab === "로그인" ? "다시 만나 반가워요." : "여행 준비를 시작해요."}
            </h2>
            <div className="tabs auth-tabs">
              {authData.view.tabs.map((value) => (
                <button
                  key={value}
                  className={tab === value ? "active" : ""}
                  onClick={() => {
                    setTab(value);
                    setError("");
                  }}
                >
                  {value}
                </button>
              ))}
            </div>
            <form onSubmit={submit}>
              {fields.map((field) => (
                <label key={field}>
                  {field}
                  <input
                    name={field}
                    type={field.includes("비밀번호") ? "password" : field === "이메일" ? "email" : "text"}
                    placeholder={field === "이메일" ? "traveler@example.com" : field}
                  />
                </label>
              ))}
              {error && <p className="field-error">{error}</p>}
              <button className="primary" disabled={loading}>
                {loading ? "잠시만요…" : tab}
              </button>
            </form>
            {tab === "로그인" && (
              <button
                className="reset"
                onClick={() => {
                  setToast("목업: 재설정 메일은 다음 단계에서 붙어요");
                  setTimeout(() => setToast(""), 2500);
                }}
              >
                비밀번호를 잊으셨나요?
              </button>
            )}
            <p className="mock-note">실제 계정은 생성되지 않는 UI 목업입니다.</p>
          </div>
        </section>
        {toast && <Toast>{toast}</Toast>}
      </Shell>
    </>
  );
}