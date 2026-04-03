from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from rest_framework.views import APIView
from core.responses import error_response, success_response
from products.serializers import MenuItemSerializer, CategorySerializer
from products.models import MenuItem, Category

CACHE_KEY = "homepage_v1"
CACHE_TTL = 60
HEALTH_CACHE_KEY = "healthcheck"

class HomepageAPIView(APIView):
    permission_classes = []  # AllowAny

    def get(self, request):
        cached = cache.get(CACHE_KEY)
        if cached:
            return success_response("Homepage fetched (cached)", data=cached)

        categories = CategorySerializer(Category.objects.all(), many=True).data
        menu_items = MenuItemSerializer(MenuItem.objects.filter(is_available=True)[:12], many=True).data
        data = {"categories": categories, "menu": menu_items}
        cache.set(CACHE_KEY, data, timeout=CACHE_TTL)
        return success_response("Homepage fetched", data=data)


class HealthCheckAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks = {"database": "ok", "cache": "ok"}

        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except OperationalError:
            checks["database"] = "error"
            return error_response("Database unavailable", errors=checks, status=503)

        try:
            cache.set(HEALTH_CACHE_KEY, "ok", timeout=5)
            if cache.get(HEALTH_CACHE_KEY) != "ok":
                raise RuntimeError("cache readback failed")
        except Exception:
            checks["cache"] = "degraded"

        return success_response("ok", data=checks)
