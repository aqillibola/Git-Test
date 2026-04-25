from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = os.getenv("AUTOPAY_APP_TITLE", "🚜 AutoPay Final System")
APP_PURPOSE = os.getenv("AUTOPAY_APP_PURPOSE", "Пул ечиш операцияларини таҳлил қилиш ва мониторинг")
APP_LANG = os.getenv("AUTOPAY_APP_LANG", "Uzbek (UTF-8)")
APP_VERSION = os.getenv("AUTOPAY_APP_VERSION", "v42")

DB_URL = os.getenv("AUTOPAY_DB_URL", "postgresql://autopay-user:tZd1mRIbKsiGP428gD7F@192.168.10.15:5432/autopay-service")

BASE_MENU = [
    "📊 Dashboard",
    "💸 Келиб тушган пул ва қолдиқ",
    "🚫 Ечилмайдиган карталар (Имтиёзли)",
    "🏆 Топ Қарздорлар",
    "📋 Қарздорлар (Барча)",
    "🕐 Пул ечишга қулай соатлар",
    "📈 Кунлик статистика (%)",
    "🐇 RabbitQM",
    "☕ AutoPay Amount Java API мониторинг",
    "🔎 ЖШШИР бўйича қидирув",
]
ADMIN_MENU = ["⚙️ Админ панель"]

PASTEL_SERVICE_COLORS = {
    "HUMO": "#BC5377",
    "UZCARD": "#7D7986",
    "Номаълум": "#C9EEE1",
}
ERROR_STATUS_COLORS = {
    "FAILED": "#D94949",
    "ERROR": "#A91D1C",
    "Номаълум": "#FDE8C9",
}

DEFAULT_START_DATE = datetime.now().date()
DEFAULT_END_DATE = datetime.now().date()
