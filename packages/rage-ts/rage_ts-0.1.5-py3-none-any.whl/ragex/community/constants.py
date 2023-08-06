# URL to Rasa license agreement
RASA_TERMS_URL = (
    "https://storage.cloud.google.com/rasa-x-releases/"
    "rasa_x_ce_license_agreement.pdf"
)

WELCOME_PAGE_URL = "https://gitlab.com/rageoflove/rage-ts"

# Key in global config file which contains whether the user agreed to the Rasa license
CONFIG_FILE_TERMS_KEY = "terms_accepted"

# Key in global config file which contains whether the user agreed to tracking
CONFIG_FILE_METRICS_KEY = "metrics"
CONFIG_METRICS_USER = "rage_user_id"
CONFIG_METRICS_ENABLED = "enabled"
CONFIG_METRICS_DATE = "date"
CONFIG_METRICS_WELCOME_SHOWN = "welcome_shown"

API_URL_PREFIX = "/api"

COMMUNITY_PROJECT_NAME = "default"
COMMUNITY_TEAM_NAME = "rage"
COMMUNITY_USERNAME = "me"

DEFAULT_CHANNEL_NAME = "rage"
SHARE_YOUR_BOT_CHANNEL_NAME = "Tester"

JWT_METHOD = "RS256"

REQUEST_DB_SESSION_KEY = "db_session"

DEFAULT_GIT_REPOSITORY_DIRECTORY = "/app/git"

EVENT_CONSUMER_SEPARATION_ENV = "RUN_EVENT_CONSUMER_AS_SEPARATE_SERVICE"

RAGE_PRODUCTION_ENVIRONMENT = "production"

DEFAULT_RAGE_ENVIRONMENT = RAGE_PRODUCTION_ENVIRONMENT
