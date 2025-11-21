"""
Health check endpoint for Azure App Service and monitoring.
"""
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Azure App Service health checks and monitoring.
    
    Returns:
        - 200 OK: Application and database are healthy
        - 503 Service Unavailable: Application or database is unhealthy
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'service': 'mha-ott'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'mha-ott'
        }, status=503)

