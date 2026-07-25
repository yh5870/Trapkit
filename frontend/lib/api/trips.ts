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

/** 수화물 규정 플래그. 규정과 무관한 일반 물품은 null. */
export type BaggageFlag = 'carry_on_only' | 'checked_only' | 'restricted';

/** 주의사항 신뢰도. check_required는 출발 전 재확인이 필요함을 뜻한다. */
export type CautionConfidence = 'stable' | 'check_required';

export interface Caution {
  category: string;
  text: string;
  confidence: CautionConfidence;
}

export interface BaggageSummaryEntry {
  category: string;
  count: number;
}

export interface TripItem {
  id: string;
  /** 목록 조회(GET /api/v1/items/:tripId) 응답의 개별 아이템에는 포함되지 않는다. */
  trip_id?: string;
  category: string;
  name: string;
  quantity: string | null;
  tip: string | null;
  baggage_flag: BaggageFlag | null;
  source: 'ai' | 'user';
  checked: boolean;
  sort_order?: number;
}

export interface Trip {
  id: string;
  title: string;
  destination: string;
  /** 백엔드는 list[str]로 반환한다 (TripResponse.purpose). */
  purpose: string[];
  user_id: string;
  duration_nights: number | null;
  departure_month: number | null;
  companions: string | null;
  cautions: Caution[];
  baggage_summary: BaggageSummaryEntry[];
  created_at: string;
  updated_at: string;
  /**
   * 진행률. 백엔드가 조회 시점에 GROUP BY로 집계한다 (DB 저장 아님).
   * GET /trips, GET /trips/:id 에만 채워지고 POST/PATCH 응답에서는 0이므로
   * 쓰기 응답으로 목록 상태를 통째로 덮어쓰지 말 것.
   */
  items_count: number;
  checked_count: number;
}

export interface SSEMessage {
  status:
    | 'started'
    | 'generating'
    | 'content_generated'
    | 'creating_entity'
    | 'saving'
    | 'creating_items'
    | 'completed'
    | 'error';
  message?: string;
  content?: unknown;
  trip?: Trip;
  [key: string]: unknown;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 여행 리스트 생성 (GET - EventSource)
 * Note: 표준 EventSource는 Authorization 헤더를 직접 설정할 수 없으므로,
 * 토큰이 필요한 경우 쿼리 파라미터로 넘기거나 generateTripWithStream을 권장합니다.
 */
export function generateTripStream(
  request: TripGenerateRequest,
  accessToken?: string
): EventSource {
  const url = new URL(`${API_BASE_URL}/api/v1/trips/generate`);

  if (request.destination) url.searchParams.set('destination', request.destination);
  if (request.purpose?.length) url.searchParams.set('purpose', request.purpose.join(','));
  if (request.duration_nights) url.searchParams.set('duration_nights', String(request.duration_nights));
  if (request.departure_month) url.searchParams.set('departure_month', String(request.departure_month));
  if (request.companions) url.searchParams.set('companions', request.companions);
  
  // EventSource용 토큰 전달 (쿼리스트링 방식)
  if (accessToken) url.searchParams.set('token', accessToken);

  return new EventSource(url.toString());
}

/**
 * 여행 리스트 생성 (POST Body) - Fetch ReadableStream 기반 SSE 처리
 */
export async function generateTripWithStream(
  request: TripGenerateRequest,
  accessToken?: string,
  onMessage?: (data: SSEMessage) => void,
  onComplete?: (trip: Trip) => void,
  onError?: (error: string) => void
): Promise<void> {
  const url = `${API_BASE_URL}/api/v1/trips/generate/body/dev`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }


    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader available');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      
      // 불완전한 마지막 줄은 버퍼에 남겨둠
      buffer = lines.pop() || '';

      for (const rawLine of lines) {
        const line = rawLine.trim(); // \r 및 여백 정리
        if (line.startsWith('data:')) {
          const data = line.slice(5).trim();
          if (!data) continue;

          try {
            const message = JSON.parse(data) as SSEMessage;
            if (onMessage) onMessage(message);

            if (message.status === 'completed' && message.trip && onComplete) {
              onComplete(message.trip);
            } else if (message.status === 'error' && onError) {
              onError(message.message || 'Unknown server error');
            }
          } catch (e) {
            console.error('Failed to parse SSE JSON:', data, e);
          }
        }
      }
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown network error';
    if (onError) {
      onError(errorMsg);
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
 * 여행 제목 수정
 *
 * 주의: PATCH 응답의 items_count/checked_count는 집계되지 않아 0이다.
 * 목록 상태를 갱신할 때는 반환값 전체가 아니라 title만 반영할 것.
 */
export async function updateTripTitle(
  tripId: string,
  title: string,
  accessToken?: string
): Promise<Trip> {
  return apiPatch<Trip>(`/api/v1/trips/${tripId}`, { title }, accessToken);
}

/**
 * 여행 삭제 (체크리스트/메모도 CASCADE 삭제됨)
 */
export async function deleteTrip(tripId: string, accessToken?: string): Promise<void> {
  await apiDelete(`/api/v1/trips/${tripId}`, accessToken);
}

/**
 * Trip ID로 상세 조회
 */
export async function getTripById(tripId: string, accessToken?: string): Promise<Trip> {
  // 백엔드 API가 { trip: ... } 형태가 아닌 Trip 객체 단일을 직접 반환하므로 apiGet<Trip> 사용
  const response = await apiGet<Trip>(
    `/api/v1/trips/${tripId}`,
    accessToken
  );
  return response;
}