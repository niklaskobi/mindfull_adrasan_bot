from alembic import context

from app.core.consts import DB_URL

config = context.config

# read sqlalchemy.url from env
config.set_main_option("sqlalchemy.url", DB_URL)
