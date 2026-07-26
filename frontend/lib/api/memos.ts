/**
 * 메모 관련 API
 */
import { apiGet, apiPost, apiPatch, apiDelete } from '../api-client';

export interface Memo {
  id: string;
  trip_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

/**
 * Trip ID로 모든 메모 조회
 */
export async function getMemosByTripId(tripId: string, accessToken?: string): Promise<Memo[]> {
  const response = await apiGet<{ memos: Memo[]; total: number }>(
    `/api/v1/memos/${tripId}`,
    accessToken
  );
  return response.memos;
}

/**
 * 메모 생성
 */
export async function createMemo(
  tripId: string,
  content: string,
  accessToken?: string
): Promise<Memo> {
  return apiPost<Memo>(
    '/api/v1/memos',
    { trip_id: tripId, content },
    accessToken
  );
}

/**
 * 메모 수정
 */
export async function updateMemo(
  memoId: string,
  content: string,
  accessToken?: string
): Promise<Memo> {
  return apiPatch<Memo>(
    `/api/v1/memos/${memoId}`,
    { content },
    accessToken
  );
}

/**
 * 메모 삭제
 */
export async function deleteMemo(memoId: string, accessToken?: string): Promise<void> {
  await apiDelete(`/api/v1/memos/${memoId}`, accessToken);
}