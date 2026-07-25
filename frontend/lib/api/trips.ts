/**
 * 여행 리스트 관련 API
 */
import { apiGet, apiPost, apiPatch, apiDelete } from '../api-client';

export interface TripGenerateRequest {
  destination: string;
  purpose: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
}

export interface TripItem {
  id: string;
  trip_id: string;
  category: string;
  name: string;
  quantity: string | null;
  tip: string | null;
  baggage_flag: string | null;
  source: 'ai' | 'user';
  checked: boolean;
}

export interface Trip {
  id: string;
  title: string;
  destination: string;
  purpose: string;
  user_id: string;
  duration_nights: number | null;
  departure_month: number | null;
  companions: string | null;
  cautions: Array<{ category: string; text: string }>;
  baggage_summary: Array<{ item: string; rule: string }>;
  created_at: string;
  updated_at: string;
  items_count?: number;
}

export interface SSEMessage {
  status: 'started' | 'generating' | 'content_generated' | 'creating_entity' | 'saving' | 'creating_items' | 'completed' | 'error';
  message?: string;
  content?: unknown;
  trip?: Trip;
  [key: string]: unknown;
}

/**
 * 여행 리스트 생성 (SSE 스트리밍)
 */
export function generateTripStream(
  request: TripGenerateRequest,
  accessToken?: string
): EventSource {
  // 개발용 엔드포인트는 POST body를 사용하지만 EventSource는 GET만 지원
  // 임시로 쿼리 파라미터 버전 사용
  const url = new URL(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/trips/generate`);

  if (request.destination) {
    url.searchParams.set('destination', request.destination);
  }
  if (request.purpose && request.purpose.length > 0) {
    url.searchParams.set('purpose', request.purpose.join(','));
  }
  if (request.duration_nights) {
    url.searchParams.set('duration_nights', String(request.duration_nights));
  }
  if (request.departure_month) {
    url.searchParams.set('departure_month', String(request.departure_month));
  }
  if (request.companions) {
    url.searchParams.set('companions', request.companions);
  }

  return new EventSource(url.toString());
}

/**
 * 여행 리스트 생성 (POST Body) - SSE 스트림 처리
 * Note: EventSource는 GET만 지원하므로 fetch 스트리밍 사용
 */
export async function generateTripWithStream(
  request: TripGenerateRequest,
  accessToken?: string,
  onMessage?: (data: SSEMessage) => void,
  onComplete?: (trip: Trip) => void,
  onError?: (error: string) => void
): Promise<void> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${apiUrl}/api/v1/trips/generate/body/dev`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { 'Authorization': `Bearer ${accessToken}` }),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // SSE 스트림 처리
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const message = JSON.parse(data) as SSEMessage;
            if (onMessage) onMessage(message);

            if (message.status === 'completed' && message.trip && onComplete) {
              onComplete(message.trip);
            } else if (message.status === 'error' && onError) {
              onError(message.message || 'Unknown error');
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', data, e);
          }
        }
      }
    }
  } catch (error) {
    if (onError) {
      onError(error instanceof Error ? error.message : 'Unknown error');
    }
    throw error;
  }
}

/**
 * Trip ID로 아이템 목록 조회
 */
export async function getTripItems(tripId: string, accessToken?: string): Promise<TripItem[]> {
  const response = await apiGet<{ items: TripItem[] }>(
    `/api/v1/items/${tripId}`,
    accessToken
  );
  return response.items;
}

/**
 * 아이템 체크 상태 토글
 */
export async function toggleItemCheck(
  itemId: string,
  checked: boolean,
  accessToken?: string
): Promise<TripItem> {
  return apiPatch<TripItem>(
    `/api/v1/items/${itemId}`,
    { checked },
    accessToken
  );
}

/**
 * 아이템 추가
 */
export async function addTripItem(
  tripId: string,
  item: Omit<TripItem, 'id' | 'trip_id' | 'checked'>,
  accessToken?: string
): Promise<TripItem> {
  return apiPost<TripItem>(
    '/api/v1/items',
    { trip_id: tripId, ...item },
    accessToken
  );
}

/**
 * 아이템 삭제
 */
export async function deleteTripItem(itemId: string, accessToken?: string): Promise<void> {
  await apiDelete(`/api/v1/items/${itemId}`, accessToken);
}

/**
 * 사용자의 모든 여행 리스트 조회
 */
export async function getUserTrips(accessToken?: string): Promise<Trip[]> {
  const response = await apiGet<{ trips: Trip[] }>(
    '/api/v1/trips',
    accessToken
  );
  return response.trips;
}

/**
 * Trip ID로 상세 조회
 */
export async function getTripById(tripId: string, accessToken?: string): Promise<Trip> {
  const response = await apiGet<{ trip: Trip }>(
    `/api/v1/trips/${tripId}`,
    accessToken
  );
  return response.trip;
}