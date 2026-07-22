"""캐싱이 적용된 Trip 조회 서비스."""

import json
from typing import Any

from app.application.services.trip_query_service import TripQueryService
from app.core.redis import cache_delete, cache_get, cache_set


class CachedTripQueryService(TripQueryService):
    """캐싱이 적용된 Trip 조회 서비스.

    Trip 조회 결과를 Redis에 캐싱하여 DB 쿼리를 줄입니다.
    """

    # 캐시 키 접두사
    CACHE_KEY_PREFIX = "trip:"
    USER_TRIPS_CACHE_KEY = "user_trips:"

    # 캐시 TTL (초)
    CACHE_TTL = 3600  # 1시간

    async def get_user_trips(self, user_id: str) -> list[Any]:
        """사용자의 모든 Trip 조회 (캐싱 적용).

        Args:
            user_id: 사용자 ID

        Returns:
            Trip 리스트
        """
        cache_key = f"{self.USER_TRIPS_CACHE_KEY}{user_id}"

        # 캐시에서 조회
        cached_data = await cache_get(cache_key)
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                # 캐시 손상 시 무시하고 DB 조회
                pass

        # DB 조회
        trips = await super().get_user_trips(user_id)

        # 직렬화 (Trip 객체를 dict로 변환)
        trips_data = [
            {
                "id": str(trip.id.value),
                "title": trip.title,
                "destination": trip.destination,
                "purpose": trip.purpose,
                "user_id": trip.user_id,
                "duration_nights": trip.duration_nights,
                "departure_month": trip.departure_month,
                "companions": trip.companions,
                "cautions": trip.cautions,
                "baggage_summary": trip.baggage_summary,
                "created_at": trip.created_at.isoformat(),
                "updated_at": trip.updated_at.isoformat(),
            }
            for trip in trips
        ]

        # 캐시 저장
        await cache_set(cache_key, json.dumps(trips_data), self.CACHE_TTL)

        return trips

    async def get_trip_by_id(self, trip_id: str) -> Any | None:
        """ID로 Trip 조회 (캐싱 적용).

        Args:
            trip_id: Trip ID

        Returns:
            Trip 또는 None
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}{trip_id}"

        # 캐시에서 조회
        cached_data = await cache_get(cache_key)
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                # 캐시 손상 시 무시하고 DB 조회
                pass

        # DB 조회
        trip = await super().get_trip_by_id(trip_id)

        if trip is None:
            return None

        # 직렬화
        trip_data = {
            "id": str(trip.id.value),
            "title": trip.title,
            "destination": trip.destination,
            "purpose": trip.purpose,
            "user_id": trip.user_id,
            "duration_nights": trip.duration_nights,
            "departure_month": trip.departure_month,
            "companions": trip.companions,
            "cautions": trip.cautions,
            "baggage_summary": trip.baggage_summary,
            "created_at": trip.created_at.isoformat(),
            "updated_at": trip.updated_at.isoformat(),
        }

        # 캐시 저장
        await cache_set(cache_key, json.dumps(trip_data), self.CACHE_TTL)

        return trip

    async def invalidate_user_trips_cache(self, user_id: str) -> None:
        """사용자의 Trip 목록 캐시 무효화.

        사용자가 Trip을 생성/수정/삭제할 때 호출하여 캐시를 갱신합니다.

        Args:
            user_id: 사용자 ID
        """
        cache_key = f"{self.USER_TRIPS_CACHE_KEY}{user_id}"
        await cache_delete(cache_key)

    async def invalidate_trip_cache(self, trip_id: str) -> None:
        """특정 Trip 캐시 무효화.

        Trip을 수정/삭제할 때 호출하여 캐시를 갱신합니다.

        Args:
            trip_id: Trip ID
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}{trip_id}"
        await cache_delete(cache_key)
