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
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    nickname: string;
    created_at: string;
  };
}

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

/**
 * 로그인
 */
export async function login(request: LoginRequest): Promise<AuthResponse> {
  return apiPost<AuthResponse>('/api/auth/login', request);
}

/**
 * 회원가입
 */
export async function signup(request: SignupRequest): Promise<AuthResponse> {
  return apiPost<AuthResponse>('/api/auth/signup', request);
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