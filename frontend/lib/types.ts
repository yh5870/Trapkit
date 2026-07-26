/* eslint-disable @typescript-eslint/no-explicit-any */

// ============ 인증 관련 ============
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
}

export interface UserResponse {
  id: string;
  email: string;
  nickname: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// ============ 수화물 체커 관련 ============
export interface VerdictResponse {
  verdict: 'allowed' | 'conditional' | 'forbidden';
  label: string;
  reason: string;
  emoji: string;
  color_code: string;
  is_allowed: boolean;
  is_forbidden: boolean;
}

export interface BaggageCheckRequest {
  airline: string;
  product: string;
  value?: number;
  unit?: string;
}

export interface BaggageCheckResponse {
  carry_on: VerdictResponse;
  checked: VerdictResponse;
  checked_at: string;
}

// ============ 트립 관련 ============
export interface TripGenerateRequest {
  destination: string;
  purpose: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
}

export interface TripCreateRequest {
  title: string;
  destination: string;
  purpose: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions?: string[];
  baggage_summary?: string[];
}

export interface TripUpdateRequest {
  title?: string;
  destination?: string;
  purpose?: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions?: string[];
  baggage_summary?: string[];
}

export interface TripListResponse {
  trips: Trip[];
  total: number;
}

export interface Trip {
  id: string;
  title: string;
  destination: string;
  purpose: string[];
  user_id: string;
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions: string[];
  baggage_summary: string[];
  created_at: string;
  updated_at: string;
}

export interface SSEEvent {
  status: 'started' | 'generating' | 'content_generated' | 'creating' | 'saving' | 'completed' | 'error';
  message?: string;
  destination?: string;
  content?: {
    cautions: string[];
    baggage_summary: string[];
  };
  trip?: Trip;
}

// ============ 아이템 관련 ============
export interface AddItemCommand {
  trip_id: string;
  category: string;
  name: string;
  quantity?: string;
  tip?: string;
  baggage_flag?: string;
  source?: string;
}

export interface UpdateItemCommand {
  name?: string;
  quantity?: string;
  tip?: string;
  baggage_flag?: string;
  checked?: boolean;
}

export interface CheckItemCommand {
  checked: boolean;
}

export interface UpdateSortOrderCommand {
  new_order: number;
}

export interface Item {
  id: string;
  trip_id: string;
  category: string;
  name: string;
  quantity: string;
  tip?: string;
  baggage_flag: string;
  source?: string;
  checked: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ItemsByTripResponse {
  trip_id: string;
  items: Item[];
  total: number;
  checked: number;
  pending: number;
}

// ============ 메모 관련 ============
export interface Memo {
  id: string;
  trip_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface AddMemoCommand {
  trip_id: string;
  content: string; // 최대 2,000자
}

export interface UpdateMemoCommand {
  content: string; // 최대 2,000자
}

export interface MemosByTripResponse {
  trip_id: string;
  memos: Memo[];
  total: number;
}

// ============ 공통 ============
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}