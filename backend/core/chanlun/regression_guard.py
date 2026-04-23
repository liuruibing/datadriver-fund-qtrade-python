"""Lightweight regression guard for Chanlun history responses.

Run from the backend directory:

    python -m core.chanlun.regression_guard
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class HistorySample:
    symbol: str
    resolution: str
    countback: int = 50


SAMPLES = (
    HistorySample("000001.SZ", "1D"),
    HistorySample("000001.SZ", "1W"),
    HistorySample("000001.SZ", "1M"),
    HistorySample("000001.SZ", "3M"),
)

REQUIRED_KEYS = {
    "s",
    "t",
    "o",
    "h",
    "l",
    "c",
    "v",
    "bis",
    "bi_zss",
    "mmds",
    "xds",
    "zsds",
    "xd_zss",
    "zsd_zss",
    "bcs",
    "update",
    "chart_color",
    "update_time",
    "last_k_time",
    "_perf",
}


def _setup_django() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
    import django

    django.setup()


def _assert_history_shape(payload: dict, sample: HistorySample) -> None:
    missing = REQUIRED_KEYS - set(payload)
    if missing:
        raise AssertionError(f"{sample.symbol} {sample.resolution} missing keys: {sorted(missing)}")

    status = payload.get("s")
    if status not in {"ok", "no_data"}:
        raise AssertionError(f"{sample.symbol} {sample.resolution} invalid status: {status!r}")
    if status == "no_data":
        return

    length_keys = ("t", "o", "h", "l", "c", "v")
    lengths = {key: len(payload.get(key, [])) for key in length_keys}
    if len(set(lengths.values())) != 1:
        raise AssertionError(f"{sample.symbol} {sample.resolution} mismatched kline lengths: {lengths}")
    if lengths["t"] == 0:
        raise AssertionError(f"{sample.symbol} {sample.resolution} returned empty ok payload")

    for key in ("bis", "bi_zss", "mmds", "xds", "zsds", "xd_zss", "zsd_zss", "bcs"):
        if not isinstance(payload.get(key), list):
            raise AssertionError(f"{sample.symbol} {sample.resolution} {key} must be list")

    perf = payload.get("_perf")
    if not isinstance(perf, dict) or "bs_calc_ms" not in perf:
        raise AssertionError(f"{sample.symbol} {sample.resolution} missing perf.bs_calc_ms")


def _assert_algorithm_sources() -> None:
    from core.chanlun.algorithms import get_zs_seq
    from core.chanlun.ai_algorithms import get_zs_seq as ai_get_zs_seq

    if get_zs_seq.__module__ != "core.chanlun.zhongshu":
        raise AssertionError(
            f"main get_zs_seq should come from core.chanlun.zhongshu, got {get_zs_seq.__module__}"
        )
    if ai_get_zs_seq.__module__ != "ZS_sig_ai":
        raise AssertionError(f"AI get_zs_seq should come from ZS_sig_ai, got {ai_get_zs_seq.__module__}")


def main() -> None:
    _setup_django()

    from dvadmin.selection.views.chanlun import get_history_data
    from core.chanlun.utils import resolution_to_freq

    _assert_algorithm_sources()

    for sample in SAMPLES:
        freq = resolution_to_freq(sample.resolution)
        if freq is None:
            raise AssertionError(f"Unsupported resolution in guard: {sample.resolution}")
        payload = get_history_data(sample.symbol, freq, countback=sample.countback)
        _assert_history_shape(payload, sample)
        print(
            f"OK {sample.symbol} {sample.resolution}: "
            f"status={payload.get('s')} bars={len(payload.get('t', []))} "
            f"bis={len(payload.get('bis', []))} mmds={len(payload.get('mmds', []))}"
        )


if __name__ == "__main__":
    main()
