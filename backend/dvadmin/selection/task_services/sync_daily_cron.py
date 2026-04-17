# ============================================================
# A股全量股票 日终全频段更新脚本
# 
# 功能:
#   - 专门用于每日收盘后的定时任务（Crontab/计划任务）
#   - 每天自动创建一个带日期后缀的进度文件（防止和昨天冲突）
#   - 获取沪深两市所有股票列表（排除北交所）
#   - 同步当天的 daily, weekly, monthly, 5min, 30min K线数据
#   - 只会抓取[今天]的数据增量覆盖更新进数据库里面
#
# 使用方法:
#   python sync_daily_cron.py
#
# 环境变量:
#   SYNC_DATE=20240301 强制拉取某一天的全频段数据（默认是系统当前日期）
# ============================================================

import os
import sys
import time
import json
import socket
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine, text

# 忽略FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 绕过本机代理 ---
def disable_http_proxy_for_tushare():
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(k, None)
    os.environ["NO_PROXY"] = "localhost,127.0.0.1,api.waditu.com"
    os.environ["no_proxy"] = os.environ["NO_PROXY"]
    socket.setdefaulttimeout(60)

disable_http_proxy_for_tushare()

# ============================================================
# 配置
# ============================================================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.1.207'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'datadriver'),
    'password': os.getenv('DB_PASSWORD', 'datadriver'),
    'database': os.getenv('DB_NAME', 'datadriver'),
}

TUSHARE_TOKEN = os.getenv(
    'TUSHARE_TOKEN',
    'ea8e4ada23d2aa40d031cbdbb6ce73d9877caeb409b0a82424ac3e66',
)

KLINE_TABLE = 'stock_kline'
SYNC_TABLE = 'sync_log'

# 前复权
ADJ_TYPE = "qfq"

# 指定获取的周期频段
PERIODS = ['daily', 'weekly', 'monthly', '5min', '30min']

TARGET_DATE = os.getenv("SYNC_DATE", datetime.now().strftime("%Y%m%d")).strip()

# 每天生成独立的进度文件，保证每日任务能顺畅重跑
PROGRESS_FILE = Path(__file__).parent / f"sync_progress_{TARGET_DATE}.json"

# API调用间隔（秒）- Tushare有频率限制，增加了分钟级数据后可能需要更谨慎
API_DELAY = 0.15

# 重试次数
MAX_RETRIES = 3

# 初始化Tushare
pro = ts.pro_api(TUSHARE_TOKEN)


def get_engine():
    return create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def load_progress():
    """加载进度"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"completed": [], "failed": [], "last_index": 0}


def save_progress(progress):
    """保存进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def get_all_stocks():
    """获取A股所有股票列表（仅上海SH和深圳SZ，排除北交所BJ）"""
    print("正在获取A股股票列表...")
    
    # 获取所有上市股票
    df = pro.stock_basic(
        exchange='',
        list_status='L',
        fields='ts_code,symbol,name,area,industry,market,list_date'
    )
    
    if df is None or df.empty:
        print("获取股票列表失败！")
        return []
    
    # 只保留上海(SH)和深圳(SZ)的股票，排除北交所(BJ)
    df = df[df['ts_code'].str.endswith(('.SH', '.SZ'))]
    
    # 按ts_code排序
    df = df.sort_values('ts_code').reset_index(drop=True)
    
    print(f"共获取到 {len(df)} 只股票（仅沪深两市）")
    return df['ts_code'].tolist()


def fetch_kline_with_retry(ts_code, period, start_date, end_date, retries=MAX_RETRIES):
    """获取K线数据，带重试"""
    # 扩展：加入了 5min 和 30min 映射
    freq_map = {
        'daily': 'D', 
        'weekly': 'W', 
        'monthly': 'M', 
        '5min': '5min', 
        '30min': '30min'
    }
    freq = freq_map.get(period)
    
    for attempt in range(retries):
        try:
            df = ts.pro_bar(
                api=pro,
                ts_code=ts_code,
                asset="E",
                freq=freq,
                adj=ADJ_TYPE,
                start_date=start_date,
                end_date=end_date,
            )
            return df
        except Exception as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"      [{period}] 重试 {attempt + 1}/{retries}，等待 {wait_time}s... ({e})")
                time.sleep(wait_time)
            else:
                raise e
    return None


def normalize_kline_df(df, period):
    """标准化K线数据"""
    if df is None or df.empty:
        return None

    # Tushare 日级以上返回 trade_date, 分钟级通常返回 trade_time 字段
    if 'trade_date' in df.columns:
        df = df.rename(columns={'trade_date': 'trade_time'})
        
    if 'trade_time' not in df.columns:
        return None

    # 时间解析兼顾 yyyyMMdd 和 yyyy-MM-dd HH:mm:ss
    df['trade_time'] = pd.to_datetime(df['trade_time'])

    # 统一提取逻辑：
    # 将除了 daily 之外的股票周期（W/M/5min/30min）通常返回的元/股转换成千元/手
    if period in ['weekly', 'monthly', '5min', '30min']:
        if 'vol' in df.columns:
            df['vol'] = df['vol'] / 100  # 股 -> 手
        if 'amount' in df.columns:
            df['amount'] = df['amount'] / 1000  # 元 -> 千元

    now = datetime.now()
    df['period'] = period
    df['created_at'] = now
    df['updated_at'] = now

    columns = [
        'ts_code', 'trade_time', 'period',
        'open', 'high', 'low', 'close',
        'vol', 'amount',
        'created_at', 'updated_at',
    ]

    return df[[c for c in columns if c in df.columns]]


def upsert_kline(df, ts_code, period, engine):
    """插入或更新K线数据（支持增量替换）"""
    if df is None or df.empty:
        return 0

    rows = df.to_dict(orient='records')

    with engine.begin() as conn:
        conn.execute(
            text(f"""
                INSERT INTO {KLINE_TABLE}
                (ts_code, trade_time, period, open, high, low, close, vol, amount, created_at, updated_at)
                VALUES
                (:ts_code, :trade_time, :period, :open, :high, :low, :close, :vol, :amount, :created_at, :updated_at)
                ON CONFLICT (ts_code, trade_time, period)
                DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    vol = EXCLUDED.vol,
                    amount = EXCLUDED.amount,
                    updated_at = EXCLUDED.updated_at
            """),
            rows,
        )

        conn.execute(
            text(f"""
                INSERT INTO {SYNC_TABLE} (ts_code, period, last_sync_time, sync_at)
                VALUES (:ts_code, :period, :last_sync_time, :sync_at)
                ON CONFLICT (ts_code, period)
                DO UPDATE SET
                    last_sync_time = EXCLUDED.last_sync_time,
                    sync_at = EXCLUDED.sync_at
            """),
            {
                'ts_code': ts_code,
                'period': period,
                'last_sync_time': df['trade_time'].max(),
                'sync_at': datetime.now(),
            },
        )

    return len(df)


def sync_stock(ts_code, periods, sync_date, engine):
    """
    同步单只股票当日的所有设定周期数据
    日更脚本直接使用 sync_date 作为 start 和 end
    """
    total_rows = 0
    
    for period in periods:
        try:
            # 日更：只需拉取当天增量即可
            start_date = sync_date
            end_date = sync_date

            df = fetch_kline_with_retry(ts_code, period, start_date, end_date)
            df = normalize_kline_df(df, period)
            
            count = upsert_kline(df, ts_code, period, engine)
            total_rows += count
            if count > 0:
                print(f"    {period}: +{count} 条记录")
        except Exception as e:
            print(f"    {period}: 拉取/写入异常 - {e}")
        
        # 满足各频段Tushare的频率控制限制
        time.sleep(API_DELAY)
    
    return total_rows


def main():
    print("=" * 70)
    print("A股全量股票 日更全频段 数据同步计划任务")
    print("=" * 70)
    print(f"目标日期: {TARGET_DATE}")
    print(f"抓取频段: {PERIODS}")
    print(f"数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"进度缓存文件: {PROGRESS_FILE}")
    print("=" * 70)
    
    # 获取股票列表
    all_stocks = get_all_stocks()
    if not all_stocks:
        print("无法获取股票列表，退出")
        return
    
    # 加载今天这批的缓存进度
    progress = load_progress()
    completed_set = set(progress.get("completed", []))
    
    # 对接中断索引
    start_index = progress.get("last_index", 0)
    
    print(f"\n全量A股沪深数: {len(all_stocks)}")
    print(f"今日已完成数: {len(completed_set)}")
    print(f"本次切入点索引: {start_index}")
    print()
    
    engine = get_engine()
    
    total_synced = 0
    start_time = datetime.now()
    
    try:
        for i in range(start_index, len(all_stocks)):
            ts_code = all_stocks[i]
            
            # 跳过今日已经同步跑完的
            if ts_code in completed_set:
                continue
            
            # 耗时预测与打印
            elapsed = (datetime.now() - start_time).total_seconds()
            done_count = i - start_index + 1
            if done_count > 1 and elapsed > 0:
                rate = done_count / elapsed  # 每秒跑完的股票数
                remaining = len(all_stocks) - i - 1
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_str = str(timedelta(seconds=int(eta_seconds)))
            else:
                eta_str = "计算中..."
            
            print(f"[{i+1}/{len(all_stocks)}] {ts_code} (今日进度排队，预计还需: {eta_str})")
            
            try:
                # 触发五频段同拉
                rows = sync_stock(ts_code, PERIODS, TARGET_DATE, engine)
                total_synced += rows
                
                # 记录成功进度
                completed_set.add(ts_code)
                progress["completed"] = list(completed_set)
                progress["last_index"] = i + 1
                
                # 每10个执行一次保存落地，防退出
                if (i + 1) % 10 == 0:
                    save_progress(progress)
                    
            except Exception as e:
                print(f"  抛错: {e}")
                progress["failed"].append({"ts_code": ts_code, "error": str(e), "time": datetime.now().isoformat()})
                save_progress(progress)
                
            # 再补一次限流保护等待
            time.sleep(API_DELAY)
            
    except KeyboardInterrupt:
        print("\n\n用户终止任务，已在自动保存当前进度...")
        progress["last_index"] = i
        save_progress(progress)
        print(f"进度保全完毕！下次将安全从索引 {i} 重启任务")
        
    # 周期结束后执行最终保存
    save_progress(progress)
    
    elapsed = datetime.now() - start_time
    print()
    print("=" * 70)
    print(f"日期 {TARGET_DATE} 同步周期结束!")
    print("=" * 70)
    print(f"总耗时: {elapsed}")
    print(f"写入/更新记录数: {total_synced}")
    print(f"成功覆盖股票数: {len(completed_set)}")
    print(f"频发失败股票数: {len(progress.get('failed', []))}")


if __name__ == '__main__':
    main()
