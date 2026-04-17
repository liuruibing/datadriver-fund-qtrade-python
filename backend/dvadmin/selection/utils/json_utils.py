import json
from decimal import Decimal
import datetime

def _dt_to_str(dt) -> str | None:
    if dt is None:
        return None
    if isinstance(dt, datetime.datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(dt, datetime.date):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt)

def _json_safe(val):
    if val is None:
        return "-"
    if isinstance(val, (int, float, Decimal)):
        try:
            return round(float(val), 3)
        except:
            return str(val)
    if isinstance(val, (datetime.datetime, datetime.date)):
        return _dt_to_str(val)
    return str(val)
