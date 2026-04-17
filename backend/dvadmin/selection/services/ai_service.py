import requests
import json
from django.conf import settings

class AIService:
    @staticmethod
    def analyze_chanlun(symbol: str, freq: str, chanlun_data: dict):
        """
        调用 DeepSeek API 进行缠论分析 (官方对齐版)
        """
        import os
        # 1. 优先尝试从 settings (env.py) 读取
        api_key = getattr(settings, "DEEPSEEK_API_KEY", None)
        # 2. 如果 settings 为空，尝试直接从 OS 环境变量读取 (兼容性保证)
        if not api_key:
            api_key = os.environ.get("DEEPSEEK_API_KEY")

        base_url = getattr(settings, "DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = getattr(settings, "DEEPSEEK_MODEL", "deepseek-reasoner")

        if not api_key:
            return {"error": "未检测到 DEEPSEEK_API_KEY。请确保已在 OS 环境变量或 env.py 中配置。"}

        # 1. 提取基础信息
        bi_list = chanlun_data.get("bi", [])[-9:]
        seg_list = chanlun_data.get("seg", [])[-3:]  # 取最新3条线段
        zs_all = chanlun_data.get("zs", [])
        zs_list = zs_all[-4:] if len(zs_all) > 2 else zs_all  # 取最新4个中枢，2个及以下则全取
        current_price = chanlun_data.get("current_price", "-")
        current_dt = chanlun_data.get("current_dt", "-")

        # 兜底处理：如果没有线段，提示AI使用笔数据进行分析
        if not seg_list:
            seg_note = "\n**注意：当前走势暂未形成有效线段，以下分析将基于笔数据进行**\n"
        else:
            seg_note = ""

        # 2. 构建笔表格
        bi_table = "| 起始时间 | 结束时间 | 方向 | 价格区间 | 买点 | 背驰 |\n"
        bi_table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

        for b in bi_list:
            vals = f"{b['start_val']} - {b['end_val']}"
            bi_table += f"| {b['start_dt']} | {b['end_dt']} | {b['direction']} | {vals} | {b['mark']} | {b['div']} |\n"

        # 3. 构建线段表格 (官方模块)
        seg_table = "| 起始时间 | 结束时间 | 方向 | 价格区间 | 买点 | 背驰 |\n"
        seg_table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for s in seg_list:
            vals = f"{s['start_val']} - {s['end_val']}"
            seg_table += f"| {s['start_dt']} | {s['end_dt']} | {s['direction']} | {vals} | {s['mark']} | {s['div']} |\n"

        # 4. 中枢信息 (按级别公式展示)
        # 分析最新两个中枢的位置关系
        def get_zs_relation(zs1, zs2):
            """判断两个中枢的位置关系"""
            if not zs1 or not zs2:
                return "标准中枢"
            zg1, zd1 = float(zs1.get('zg', 0)), float(zs1.get('zd', 0))
            zg2, zd2 = float(zs2.get('zg', 0)), float(zs2.get('zd', 0))
            # 中枢重叠：当前中枢的高低点与前一个中枢有重叠
            if zg2 >= zd1 and zd2 <= zg1:
                return "中枢重叠"
            # 中枢扩展：当前中枢高点高于前一个高点，低点低于前一个低点
            elif zg2 > zg1 and zd2 < zd1:
                return "中枢扩展"
            # 中枢震荡向上：两个中枢区间没有重叠，当前中枢整体上移
            elif zd2 > zd1 and zg2 > zg1:
                return "中枢上移"
            # 中枢震荡向下：两个中枢区间没有重叠，当前中枢整体下移
            elif zd2 < zd1 and zg2 < zg1:
                return "中枢下移"
            else:
                return "标准中枢"

        # 获取中枢关系描述
        if len(zs_list) >= 2:
            zs_relation = get_zs_relation(zs_list[-2], zs_list[-1])
            zs_type = "中枢震荡（需结合线段方向判断趋势）"
        elif len(zs_list) == 1:
            zs_relation = "单一中枢"
            zs_type = "中枢构筑中"
        else:
            zs_relation = "无中枢"
            zs_type = "走势中"

        zs_info = f"中枢类型：{zs_type}\n最新中枢位置关系：{zs_relation}\n"
        # 修正列名：gg=最高点(最高高点)，dd=最低点(最低低点)，zg=中枢上沿，zd=中枢下沿
        zs_info += "| 起始时间 | 结束时间 | 类型 | 最高点(gg) | 最低点(dd) | 中枢上沿(zg) | 中枢下沿(zd) | 级别 | 笔数 |\n"
        zs_info += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for z in zs_list:
            line_num = z.get('line_num', z.get('level', 1) * 9)
            zs_info += f"| {z['start_dt']} | {z['end_dt']} | 震荡中枢 | {z['gg']} | {z['dd']} | {z['zg']} | {z['zd']} | {z['level']} | {line_num} |\n"

        # 5. 组装Prompt：分为两部分，显示给用户的只包含数据，传给AI的包含完整要求
        # 页面显示用的Prompt（仅数据部分）
        display_prompt = f"""
# 当前品种
代码/名称：{symbol}
数据周期：{freq}
当前时间：{current_dt}
最新价格：{current_price}

# 最新的 {len(bi_list)} 条缠论笔数据
（价格区间：起点价 - 终点价 | 买点：买卖点类型（一买/二买/三买/类二买等） | 背驰：仅一买/一卖时标注趋势背驰）
{bi_table}
{seg_note}
# 最新的 {len(seg_list)} 条缠论线段数据
（价格区间：起点价 - 终点价 | 买点：买卖点类型 | 背驰：是否存在线段背驰）
{seg_table}

# 中枢信息
{zs_info}

数据说明：
- 中枢级别：1表示本级别，>1表示中枢升级（计算公式: round(max([1, line_num / 9]), 2)）
- 笔数：中枢内包含的笔数量，>9表示中枢级别升级
- 最高点(gg)：中枢区间内笔的最高价
- 最低点(dd)：中枢区间内笔的最低价
- 中枢上沿(zg)：中枢区间的高点（ZG = Zone High）
- 中枢下沿(zd)：中枢区间的低点（ZD = Zone Low）
- 中枢位置关系：中枢重叠（区间重叠）、中枢扩展（高低点同时外扩）、中枢上移/下移（震荡方向）
"""

        # 传给AI的完整Prompt（数据 + 输出要求）
        full_prompt = display_prompt + f"""
---

# 输出要求
你是一个严谨的缠论分析专家，擅长多级别联调和分段逻辑推演。请严格按照以下固定结构输出缠论技术分析报告，禁止添加任何额外内容：

## 一、当前品种分析
简要说明当前品种所处的走势阶段、多空力量对比、当前价格位置。

## 二、走势结构分析
基于笔、线段、中枢数据，详细分析当前走势结构：
- 笔的走势组合和背驰情况
- 线段的走势和背驰情况
- 中枢的构筑、级别和位置关系
- 当前走势属于上涨/下跌/盘整中的哪个阶段

## 三、后续走势概率排序
至少列出2-3种可能的后续走势，按发生概率从高到低排序，每种走势需要说明：
- 走势描述
- 发生概率（百分比）
- 关键判断条件（突破/跌破哪个价位会确认）

## 四、买卖点提示
给出明确的操作建议：
- 支撑位和阻力位
- 潜在的买点和卖点位置（明确标注是一买/二买/三买/类二买等）
- 仓位建议和止损位置
- 风险提示

## 五、结论
用1-2句话总结最终的分析结论和操作建议，简洁明确。

所有内容使用Markdown格式，分析必须严谨，符合缠论理论，结论清晰可操作。
"""

        # 调用 API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个严谨的缠论分析专家，严格按照用户指定的结构输出分析报告，内容专业、严谨、符合缠论理论。"},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.3, # 降低随机性，保证分析严谨
            "stream": False
        }

        try:
            with requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=60) as response:
                # 先处理HTTP状态码错误
                if response.status_code == 401:
                    return {"error": "DeepSeek API 密钥无效，请检查系统配置", "code": 40101}
                elif response.status_code == 402:
                    return {"error": "DeepSeek 账户余额不足，请充值后再使用", "code": 40201}
                elif response.status_code == 429:
                    return {"error": "AI 服务请求过于频繁，请稍后再试", "code": 42901}
                elif response.status_code >= 500:
                    return {"error": "DeepSeek 服务端异常，请稍后再试", "code": 50001}

                response.raise_for_status()
                result_json = response.json()

                # 校验返回结果结构
                if "choices" not in result_json or not result_json["choices"]:
                    return {"error": "AI 服务返回结果格式异常：缺少 choices 字段", "code": 50002}
                first_choice = result_json["choices"][0]
                if "message" not in first_choice or "content" not in first_choice["message"]:
                    return {"error": "AI 服务返回结果格式异常：缺少 message 或 content 字段", "code": 50003}
                if "error" in result_json:
                    error_msg = result_json["error"].get("message", "未知错误")
                    return {"error": f"AI 服务返回错误：{error_msg}", "code": 50004}

                content = first_choice["message"]["content"]
                usage = result_json.get("usage", {})
                actual_model = result_json.get("model", model)

                return {
                    "prompt": display_prompt,
                    "report": content,
                    "usage": usage,
                    "model": actual_model
                }
        except requests.exceptions.ConnectionError:
            return {"error": "无法连接到 DeepSeek 服务，请检查网络配置", "code": 50301}
        except requests.exceptions.Timeout:
            return {"error": "DeepSeek 服务响应超时，请稍后重试", "code": 50401}
        except json.JSONDecodeError:
            return {"error": "AI 服务返回结果不是有效的JSON格式", "code": 50005}
        except Exception as e:
            return {"error": f"DeepSeek AI 分析请求失败: {str(e)}", "code": 50000}
