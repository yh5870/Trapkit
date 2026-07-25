/**
 * API 클라이언트 설정 및 유틸리티
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * API 요청 헤더 생성
 */
export function getHeaders(accessToken?: string): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  return headers;
}

/**
 * API 응답 에러 처리
 */
export async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * GET 요청
 */
export async function apiGet<T>(
  endpoint: string,
  accessToken?: string
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: getHeaders(accessToken),
  });
  return handleResponse<T>(response);
}

/**
 * POST 요청
 */
export async function apiPost<T>(
  endpoint: string,
  data?: unknown,
  accessToken?: string
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: getHeaders(accessToken),
    body: data ? JSON.stringify(data) : undefined,
  });
  return handleResponse<T>(response);
}

/**
 * PATCH 요청
 */
export async function apiPatch<T>(
  endpoint: string,
  data?: unknown,
  accessToken?: string
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PATCH',
    headers: getHeaders(accessToken),
    body: data ? JSON.stringify(data) : undefined,
  });
  return handleResponse<T>(response);
}

/**
 * DELETE 요청
 */
export async function apiDelete(
  endpoint: string,
  accessToken?: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
    headers: getHeaders(accessToken),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
}

/**
 * SSE (Server-Sent Events) 스트리밍
 */
export function createSSEStream<T>(
  endpoint: string,
  params?: Record<string, string>,
  accessToken?: string
): EventSource {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }

  const eventSource = new EventSource(url.toString());
  return eventSource;
}