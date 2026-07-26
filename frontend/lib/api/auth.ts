/**
 * 인증 관련 API
 */
import { useState, useEffect } from 'react';
import { apiPost, apiGet } from '../api-client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  /** 백엔드 SignupRequest 는 'nickname' 을 요구한다 ('name' 아님). */
  nickname: string;
}

/** 백엔드 UserResponse (app/schemas/auth.py) */
export interface UserResponse {
  id: string;
  email: string;
  nickname: string;
  created_at: string;
}

/** 백엔드 TokenResponse. 로그인 응답 전용. */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

/**
 * 회원가입 응답.
 * 주의: 백엔드 /signup 은 response_model=UserResponse 라 토큰을 주지 않는다.
 * 토큰이 필요하면 가입 후 별도로 login() 을 호출해야 한다.
 */
export type SignupResponse = UserResponse;

/** GET /api/auth/me 응답 = UserResponse */
export type UserProfile = UserResponse;

/**
 * 로그인
 */
export async function login(request: LoginRequest): Promise<AuthResponse> {
  return apiPost<AuthResponse>('/api/auth/login', request);
}

/**
 * 회원가입
 */
export async function signup(request: SignupRequest): Promise<SignupResponse> {
  return apiPost<SignupResponse>('/api/auth/signup', request);
}

/**
 * 회원가입 후 곧바로 로그인해 토큰까지 확보한다.
 *
 * 백엔드 /signup 이 토큰을 반환하지 않으므로, 가입 직후 로그인 화면으로
 * 되돌리지 않으려면 이 조합이 필요하다.
 */
export async function signupAndLogin(request: SignupRequest): Promise<AuthResponse> {
  await signup(request);
  return login({ email: request.email, password: request.password });
}

/**
 * 현재 사용자 프로필 조회
 */
export async function getCurrentUserProfile(accessToken: string): Promise<UserProfile> {
  return apiGet<UserProfile>('/api/auth/me', accessToken);
}

/**
 * 로그아웃 (프론트엔드에서 토큰 삭제만 처리)
 */
export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('tripkit-access-token');
    localStorage.removeItem('tripkit-user-id');
  }
}

/**
 * 로컬 스토리지에서 토큰 가져오기
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('tripkit-access-token');
  }
  return null;
}

/**
 * 토큰 저장
 */
export function setAccessToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('tripkit-access-token', token);
  }
}

/**
 * 사용자 ID 가져오기
 */
export function getUserId(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('tripkit-user-id');
  }
  return null;
}

/**
 * 사용자 ID 저장
 */
export function setUserId(userId: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('tripkit-user-id', userId);
  }
}

/**
 * 인증 상태 확인
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

/**
 * 인증 상태 훅
 */
export function useAuth() {
  const [loggedIn, setLoggedInState] = useState(false);
  const [menu, setMenu] = useState(false);

  // 인증 상태 초기화
  useEffect(() => {
    setLoggedInState(isAuthenticated());
  }, []);

  const setLoggedIn = (value: boolean) => {
    if (!value) {
      logout();
    }
    setLoggedInState(value);
    window.dispatchEvent(new Event("tripkit-auth"));
  };

  // 인증 동기화
  useEffect(() => {
    const sync = () => setLoggedInState(isAuthenticated());
    window.addEventListener("tripkit-auth", sync);
    return () => window.removeEventListener("tripkit-auth", sync);
  }, []);

  return [loggedIn, setLoggedIn, menu, setMenu] as const;
}