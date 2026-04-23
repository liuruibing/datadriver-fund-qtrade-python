"""Main Chanlun divergence helpers."""

from __future__ import annotations

from .runtime import setup_local_czsc

setup_local_czsc()

from czsc.core import CZSC, Direction
from czsc.signals.tas import update_macd_cache


def check_beichi(
    c_sdt,
    c_edt,
    b_sdt,
    b_edt,
    direction: Direction,
    czsc_obj: CZSC,
    th: int = 100,
) -> bool:
    if not (c_sdt and c_edt and b_sdt and b_edt and czsc_obj):
        return False

    cache_key = update_macd_cache(czsc_obj, fastperiod=12, slowperiod=26, signalperiod=9)

    def _bars_in_range(sdt, edt):
        bars = [x for x in czsc_obj.bars_raw if sdt <= x.dt <= edt]
        if len(bars) > 2:
            return bars[1:-1]
        return bars

    def _macd_area(sdt, edt):
        try:
            macd = [x.cache[cache_key]["macd"] for x in _bars_in_range(sdt, edt)]
        except (KeyError, AttributeError, TypeError):
            return 0.0

        if direction == Direction.Down:
            return float(abs(sum([x for x in macd if x < 0])))
        return float(sum([x for x in macd if x > 0]))

    b_area = _macd_area(b_sdt, b_edt)
    c_area = _macd_area(c_sdt, c_edt)
    return bool(b_area > 0 and c_area <= b_area * th / 100)

__all__ = ["check_beichi"]
