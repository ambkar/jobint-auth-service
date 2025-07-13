from datetime import datetime, timedelta
from models import TempCode

async def clear_expired_codes():
    now = datetime.utcnow()
    expired = await TempCode.filter(created_at__lt=now - timedelta(minutes=1)).delete()
    return expired
