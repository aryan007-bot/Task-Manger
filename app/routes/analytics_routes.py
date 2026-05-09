"""
Analytics route — returns Pandas/NumPy-computed insights for the authenticated user.
"""
from flask import Blueprint
from app.services.analytics_service import AnalyticsService
from app.middleware.auth_middleware import jwt_required_middleware, get_current_user_id
from app.utils.response_handler import success_response

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.get("")
@jwt_required_middleware
def get_analytics():
    uid = get_current_user_id()
    data = AnalyticsService.get_analytics(uid)
    return success_response(data)
