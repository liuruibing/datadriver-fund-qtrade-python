import os
import json
import time
from sqlalchemy import create_engine, text
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class TVStorageViewSet(viewsets.ViewSet):
    """
    TradingView 保存和加载图表配置的接口，按照 TradingView 协议对接 PostgreSQL 库
    挂载在 /api/selection/tradingview/storage/ 下
    """
    permission_classes = [AllowAny]

    def _get_engine(self):
        db_host = os.getenv("DB_HOST", "192.168.1.207")
        db_port = int(os.getenv("DB_PORT", "5432"))
        db_user = os.getenv("DB_USER", "datadriver")
        db_password = os.getenv("DB_PASSWORD", "datadriver")
        db_name = os.getenv("DB_NAME", "datadriver")
        return create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    def charts(self, request):
        """处理 /1.1/charts 的请求 (GET, POST, DELETE)"""
        engine = self._get_engine()
        
        if request.method == 'GET':
            # 加载图表列表或获取单个图表详情
            client = request.query_params.get('client', '')
            user = request.query_params.get('user', '')
            chart_id = request.query_params.get('chart')
            
            with engine.connect() as conn:
                if chart_id:
                    # 获取单个图表详情
                    query = text("""
                        SELECT id, name, timestamp, resolution, symbol, content
                        FROM tv_chart_layouts
                        WHERE id = :id AND client_id = :client AND user_id = :user
                    """)
                    result = conn.execute(query, {"id": chart_id, "client": client, "user": user}).fetchone()
                    
                    if result:
                        # 强制将 content 转换为纯 JSON 字符串
                        # 报错的原因是你把它注释掉了，导致下面用到了一个不存在的变量 content_str。
                        # 至于为什么之前展示为对象，是因为 PostgreSQL 的 JSONB 字段被 SQLAlchemy 取出来时会自动变成 Python 的字典 (dict)，
                        # Django 的 Response 会自动将字典进行序列化，所以前端收到的是对象。
                        # TradingView 要求 content 必须是一个 JSON 格式的字符串。
                        import json
                        content_val = result.content
                        if isinstance(content_val, (dict, list)):
                            content_str = json.dumps(content_val)
                        else:
                            content_str = str(content_val)
                        
                        data = {
                            "id": result.id,
                            "name": result.name,
                            "timestamp": result.timestamp,
                            "resolution": result.resolution,
                            "symbol": result.symbol,
                            "content": content_str
                        }
                        return Response({"status": "ok", "data": data})
                    else:
                        return Response({"status": "error", "message": "Chart not found"})
                else:
                    # 加载加载图表列表
                    query = text("""
                        SELECT id, name, timestamp, resolution, symbol
                        FROM tv_chart_layouts
                        WHERE client_id = :client AND user_id = :user
                    """)
                    result = conn.execute(query, {"client": client, "user": user})
                    
                    data = []
                    for row in result:
                        data.append({
                            "id": row.id,
                            "name": row.name,
                            "timestamp": row.timestamp,
                            "resolution": row.resolution,
                            "symbol": row.symbol
                        })
                        
                    return Response({"status": "ok", "data": data})
            
        elif request.method == 'POST':
            # 保存图表 (新建或更新)
            # data可能在query_params或者POST中
            chart_id = request.data.get('chart') or request.query_params.get('chart')
            client = request.data.get('client') or request.query_params.get('client', '')
            user = request.data.get('user') or request.query_params.get('user', '')
            name = request.data.get('name', '')
            symbol = request.data.get('symbol', '')
            resolution = request.data.get('resolution', '')
            content = request.data.get('content', '{}')
            timestamp = int(time.time())
            
            with engine.connect() as conn:
                with conn.begin():
                    if chart_id:
                        # 更新现有图表
                        update_query = text("""
                            UPDATE tv_chart_layouts
                            SET name = :name, symbol = :symbol, resolution = :resolution,
                                content = :content, timestamp = :timestamp, updated_at = CURRENT_TIMESTAMP
                            WHERE id = :id AND client_id = :client AND user_id = :user
                        """)
                        conn.execute(update_query, {
                            "name": name, "symbol": symbol, "resolution": resolution,
                            "content": content, "timestamp": timestamp,
                            "id": chart_id, "client": client, "user": user
                        })
                        return Response({"status": "ok"})
                    else:
                        # 新建图表
                        insert_query = text("""
                            INSERT INTO tv_chart_layouts (user_id, client_id, name, symbol, resolution, content, timestamp)
                            VALUES (:user, :client, :name, :symbol, :resolution, :content, :timestamp)
                            RETURNING id
                        """)
                        result = conn.execute(insert_query, {
                            "user": user, "client": client, "name": name,
                            "symbol": symbol, "resolution": resolution,
                            "content": content, "timestamp": timestamp
                        })
                        new_id = result.fetchone()[0]
                        return Response({"status": "ok", "id": new_id})

        elif request.method == 'DELETE':
            # 删除图表
            chart_id = request.query_params.get('chart')
            client = request.query_params.get('client', '')
            user = request.query_params.get('user', '')
            
            with engine.connect() as conn:
                with conn.begin():
                    delete_query = text("""
                        DELETE FROM tv_chart_layouts
                        WHERE id = :id AND client_id = :client AND user_id = :user
                    """)
                    conn.execute(delete_query, {"id": chart_id, "client": client, "user": user})
            return Response({"status": "ok"})

    def study_templates(self, request):
        """如果需要指标模板保存，预留接口"""
        return Response({"status": "ok", "data": []})
