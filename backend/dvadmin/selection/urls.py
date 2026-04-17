'''
Description: 
Author: 
Date: 2025-12-23 17:37:13
LastEditors: Please set LastEditors
LastEditTime: 2026-01-06 09:22:58
'''
from django.urls import path, re_path
from rest_framework import routers
from .views.stock_selection import StockSelectionViewSet
from .views.base_data import BaseSelectionDataView
from .views.backtest import MACDBacktradeView
from .views.tangle import TangleView
from .views.tradingview import TradingViewViewSet
from .views.chanlun import ChanlunTradingViewViewSet
from .views.tv_storage import TVStorageViewSet

# 接口路由
router = routers.SimpleRouter()

router.register(r'stock-selection', StockSelectionViewSet, basename='stock-selection')
router.register(r'stock-back', MACDBacktradeView, basename='stock-back')
router.register(r'stock-tangle', TangleView, basename='stock-tangle')

urlpatterns = [
    path(r"stock-base/", BaseSelectionDataView.as_view()),
    # TradingView UDF 端点 - 使用re_path支持带或不带尾部斜杠的访问
    re_path(r"tradingview/config/?$", TradingViewViewSet.as_view({'get': 'config'})),
    re_path(r"tradingview/symbols/?$", TradingViewViewSet.as_view({'get': 'symbols'})),
    re_path(r"tradingview/symbol_info/?$", TradingViewViewSet.as_view({'get': 'symbol_info'})),
    re_path(r"tradingview/history/?$", ChanlunTradingViewViewSet.as_view({'get': 'history'})),
    re_path(r"tradingview/search/?$", TradingViewViewSet.as_view({'get': 'search'})),
    re_path(r"tradingview/time/?$", TradingViewViewSet.as_view({'get': 'time'})),
    re_path(r"tradingview/ai_analysis/?$", ChanlunTradingViewViewSet.as_view({'post': 'ai_analysis'})),
    re_path(r"tradingview/ai_history/?$", ChanlunTradingViewViewSet.as_view({'post': 'ai_history'})),
    re_path(r"tradingview/ai_history_delete/?$", ChanlunTradingViewViewSet.as_view({'post': 'ai_history_delete'})),
    # TV 存储图表路由
    re_path(r"tradingview/storage/1.1/charts/?$", TVStorageViewSet.as_view({'get': 'charts', 'post': 'charts', 'delete': 'charts'})),
    re_path(r"tradingview/storage/1.1/study_templates/?$", TVStorageViewSet.as_view({'get': 'study_templates', 'post': 'study_templates', 'delete': 'study_templates'})),
    # Chanlun 真实 history 已统一到 /tradingview/history
]

urlpatterns += router.urls
