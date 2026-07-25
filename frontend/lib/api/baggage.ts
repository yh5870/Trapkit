/**
 * 수화물 체커 관련 API
 */
import { apiPost } from '../api-client';

export interface BaggageCheckRequest {
  airline: string;
  product: string;
  value: number;
  unit: 'ml' | 'g' | 'l' | 'kg' | 'inch' | 'cm';
}

export interface Verdict {
  verdict: 'allowed' | 'caution' | 'prohibited' | 'unknown';
  label: string;
  reason: string;
  emoji?: string;
  color_code?: string;
  is_allowed: boolean;
  is_forbidden: boolean;
}

export interface BaggageCheckResponse {
  carry_on: Verdict;
  checked: Verdict;
  checked_at: string;
}

/**
 * 수화물 규정 체크
 */
export async function checkBaggage(
  request: BaggageCheckRequest,
  accessToken?: string
): Promise<BaggageCheckResponse> {
  return apiPost<BaggageCheckResponse>(
    '/api/v1/baggage/check',
    request,
    accessToken
  );
}