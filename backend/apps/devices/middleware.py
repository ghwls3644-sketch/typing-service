import hashlib
from django.utils import timezone
from django.core.cache import cache
from .models import Client

# 동일 guest_id에 대해 DB upsert를 디바운싱하는 간격 (초)
GUEST_UPSERT_DEBOUNCE_SECONDS = 60


class GuestClientMiddleware:
    """
    모든 API 요청에서 guest_session_id를 감지하고
    devices_client 레코드를 upsert합니다.

    guest_session_id 탐색 순서:
    1. POST/PUT body의 guest_session_id
    2. GET query param의 guest_session_id
    3. X-Guest-Session-Id 헤더 (향후 확장)

    디바운싱: 동일 guest_id에 대해 60초 내 중복 DB 쓰기를 방지합니다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        guest_id = self._extract_guest_id(request)

        if guest_id:
            request.guest_session_id = guest_id
            # 캐시 기반 디바운싱: 최근 upsert 한 적 없으면 DB 기록
            cache_key = f'guest_seen:{guest_id}'
            if not cache.get(cache_key):
                self._upsert_client(guest_id, request)
                cache.set(cache_key, 1, GUEST_UPSERT_DEBOUNCE_SECONDS)
        else:
            request.guest_session_id = None

        response = self.get_response(request)
        return response

    def _extract_guest_id(self, request):
        """요청에서 guest_session_id를 추출합니다."""
        # 1. POST body
        if hasattr(request, 'data'):
            guest_id = request.data.get('guest_session_id')
            if guest_id:
                return guest_id

        # 2. Query parameter
        guest_id = request.GET.get('guest_session_id')
        if guest_id:
            return guest_id

        # 3. Header (향후 확장)
        guest_id = request.META.get('HTTP_X_GUEST_SESSION_ID')
        if guest_id:
            return guest_id

        return None

    def _upsert_client(self, guest_id, request):
        """클라이언트 레코드를 생성하거나 last_seen_at을 갱신합니다."""
        try:
            ua = request.META.get('HTTP_USER_AGENT', '')
            ua_hash = hashlib.sha256(ua.encode()).hexdigest()[:16] if ua else None

            Client.objects.update_or_create(
                guest_session_id=guest_id,
                defaults={
                    'last_seen_at': timezone.now(),
                    'ua_hash': ua_hash,
                },
            )
        except Exception:
            # DB 에러가 요청 처리를 방해하지 않도록
            pass
