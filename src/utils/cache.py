from flask_caching import Cache
from src.config.cache import cache_config
from src.app import app

cache = Cache(app.server, config=cache_config)