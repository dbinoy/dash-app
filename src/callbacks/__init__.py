from src.callbacks.filters import register_callbacks as register_filters_callbacks
from src.callbacks.summary_cards import register_callbacks as register_summary_cards_callbacks
from src.callbacks.weekly_login_trends import register_callbacks as register_weekly_login_trends_callbacks
from src.callbacks.app_usage_by_office import register_callbacks as register_app_usage_by_office_callbacks
from src.callbacks.user_activity_distribution import register_callbacks as register_user_activity_distribution_callbacks
from src.callbacks.weekly_app_popularity import register_callbacks as register_weekly_app_popularity_callbacks
from src.callbacks.data_table_view import register_callbacks as register_data_table_view_callbacks

def register_all_callbacks(app):
    register_filters_callbacks(app)
    register_summary_cards_callbacks(app)
    register_weekly_login_trends_callbacks(app)
    register_app_usage_by_office_callbacks(app)
    register_user_activity_distribution_callbacks(app)
    register_weekly_app_popularity_callbacks(app)
    register_data_table_view_callbacks(app)