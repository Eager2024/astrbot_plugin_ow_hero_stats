import os
import time
import json
import requests
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image as AstrImage, Plain

@register("ow_hero_stats", "Echo", "OW2国服数据可视化版", "2.6.0")
class OWHeroStatsPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # === 配置 ===
        self.API_URL = "https://webapi.blizzard.cn/ow-armory-server/hero_leaderboard"
        self.CURRENT_SEASON = 2
        self.CACHE_TTL = 1800  # 缓存 30 分钟
        
        # 路径设置
        self.PLUGIN_DIR = os.path.dirname(__file__)
        self.FONT_PATH = os.path.join(self.PLUGIN_DIR, "思源黑体 CN Bold.otf")
        self.ICON_DIR = os.path.join(self.PLUGIN_DIR, "icons") 
        
        # === 缓存 ===
        self.data_cache = {} 
        self.icon_cache = {} 

        # === 映射表 ===
        self.RANK_ORDER = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "GrandMaster", "Champion"]
        
        # 显示名称映射
        self.DISPLAY_CN_MAP = {
            # 段位
            -127: "所有分段", "Bronze": "青铜", "Silver": "白银", "Gold": "黄金", 
            "Platinum": "白金", "Diamond": "钻石", "Master": "大师", "GrandMaster": "宗师", "Champion": "冠军",
            # 职责
            "0": "所有职责", "1": "输出", "2": "重装", "3": "支援",
            # 排序
            "win_ratio": "胜率", "selection_ratio": "出场率", "ban_ratio": "禁用率", "kda": "KDA"
        }
        
        self.RANK_MAP = {
            "所有": -127, "全部": -127, "all": -127,
            "青铜": "Bronze", "bronze": "Bronze",
            "白银": "Silver", "silver": "Silver",
            "黄金": "Gold", "gold": "Gold",
            "白金": "Platinum", "铂金": "Platinum", "platinum": "Platinum",
            "钻石": "Diamond", "diamond": "Diamond",
            "大师": "Master", "master": "Master",
            "宗师": "GrandMaster", "grandmaster": "GrandMaster"
        }
        
        # 模糊词映射
        self.ROLE_MAP = {
            "输出": "1", "C": "1", "damage": "1",
            "重装": "2", "T": "2", "tank": "2", "坦克": "2",
            "支援": "3", "奶": "3", "辅助": "3", "support": "3",
            "所有": "0", "all": "0"
        }

        # 英雄中英文对照
        self.HERO_NAME_MAP = {
            "vendetta": "斩仇", "wuyang": "无漾", "freja": "弗蕾娅", "hazard": "骇灾", 
            "juno": "朱诺", "illari": "伊拉锐", "mauga": "毛加", "venture": "探奇", "lifeweaver": "生命之梭",
            "ana": "安娜", "kiriko": "雾子", "moira": "莫伊拉", "baptiste": "巴蒂斯特", 
            "zenyatta": "禅雅塔", "mercy": "天使", "lucio": "卢西奥", "brigitte": "布丽吉塔",
            "sigma": "西格玛", "ramattra": "拉玛刹", "orisa": "奥丽莎", "winston": "温斯顿", 
            "dva": "D.Va", "reinhardt": "莱因哈特", "zarya": "查莉娅", "roadhog": "路霸", 
            "junker-queen": "渣客女王", "doomfist": "末日铁拳", "wrecking-ball": "破坏球",
            "cassidy": "卡西迪", "genji": "源氏", "soldier-76": "士兵：76", "bastion": "堡垒", 
            "ashe": "艾什", "reaper": "死神", "sojourn": "索杰恩", "hanzo": "半藏", 
            "symmetra": "秩序之光", "pharah": "法老之鹰", "widowmaker": "黑百合", "echo": "回声", 
            "junkrat": "狂鼠", "mei": "小美", "torbjorn": "托比昂", "tracer": "猎空", "sombra": "黑影", 
            "mizuki": "瑞稀", "jetpackcat": "飞天猫", "anran": "安燃", "emre": "埃姆雷", "domina": "金驭"
        }
        self.CN_TO_HERO_ID = {v: k for k, v in self.HERO_NAME_MAP.items()}

    def _get_api_data(self, rank_code, game_mode="jingji"):
        """获取数据（带缓存）"""
        cache_key = f"{game_mode}_{self.CURRENT_SEASON}_{rank_code}"
        curr_time = time.time()
        
        if cache_key in self.data_cache:
            if curr_time - self.data_cache[cache_key]["time"] < self.CACHE_TTL:
                return self.data_cache[cache_key]["data"]
        
        try:
            params = { "game_mode": game_mode, "season": self.CURRENT_SEASON, "mmr": rank_code }
            resp = requests.get(self.API_URL, params=params, timeout=10, verify=False)
            if resp.status_code == 200:
                json_data = resp.json()
                data = json_data.get("data", []) if isinstance(json_data, dict) else json_data
                if data:
                    self.data_cache[cache_key] = {"data": data, "time": curr_time}
                return data
        except Exception as e:
            logger.error(f"OW API Error: {e}")
        return []

    def _get_hero_icon(self, hero_id):
        """读取本地英雄头像"""
        if hero_id in self.icon_cache:
            return self.icon_cache[hero_id]
        
        icon_path = os.path.join(self.ICON_DIR, f"{hero_id}.png")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA")
                img = img.resize((40, 40)) 
                self.icon_cache[hero_id] = img
                return img
            except Exception as e:
                logger.error(f"Error loading icon {hero_id}: {e}")
        
        return Image.new("RGBA", (40, 40), (0, 0, 0, 0))

    def _draw_table(self, title, headers, rows, col_widths):
        """绘图引擎"""
        BG_COLOR = (30, 33, 36)
        HEADER_BG = (40, 43, 48)
        TEXT_COLOR = (255, 255, 255)
        ACCENT_COLOR = (236, 121, 5) 
        ROW_ALT_COLOR = (35, 38, 41)
        
        row_height = 50
        header_height = 60
        title_height = 70
        padding = 20
        total_width = sum(col_widths) + padding * 2
        total_height = title_height + header_height + (len(rows) * row_height) + padding

        img = Image.new("RGB", (total_width, total_height), BG_COLOR)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype(self.FONT_PATH, 32)
            text_font = ImageFont.truetype(self.FONT_PATH, 22) 
            name_font = ImageFont.truetype(self.FONT_PATH, 20) 
            small_font = ImageFont.truetype(self.FONT_PATH, 18)
        except:
            title_font = text_font = name_font = small_font = ImageFont.load_default()

        # 1. 标题
        draw.text((padding, 15), title, font=title_font, fill=ACCENT_COLOR)
        
        # 2. 表头
        draw.rectangle([(0, title_height), (total_width, title_height + header_height)], fill=HEADER_BG)
        current_x = padding
        for i, header in enumerate(headers):
            draw.text((current_x, title_height + 15), header, font=text_font, fill=(200, 200, 200))
            current_x += col_widths[i]

        # 3. 数据行
        y = title_height + header_height
        for i, row_data in enumerate(rows):
            if i % 2 == 0:
                draw.rectangle([(0, y), (total_width, y + row_height)], fill=ROW_ALT_COLOR)
            
            current_x = padding
            
            # Rank (#)
            draw.text((current_x, y + 12), str(row_data[0]), font=text_font, fill=TEXT_COLOR)
            current_x += col_widths[0]

            # Icon + Name
            hero_id = row_data[-1] 
            if hero_id:
                icon = self._get_hero_icon(hero_id)
                img.paste(icon, (current_x, y + 5), icon)
                draw.text((current_x + 50, y + 12), str(row_data[1]), font=name_font, fill=TEXT_COLOR)
            else:
                draw.text((current_x, y + 12), str(row_data[1]), font=name_font, fill=TEXT_COLOR)
            current_x += col_widths[1]

            # Data
            for j, val in enumerate(row_data[2:-1]):
                color = TEXT_COLOR
                # 只有胜率变色 (仅当为数值列且是第一列数据时)
                if j == 0 and "%" in str(val): 
                    try:
                        num = float(str(val).replace("%", ""))
                        if num > 52.0: color = (100, 255, 100)
                        elif num < 48.0: color = (255, 100, 100)
                    except: pass
                
                draw.text((current_x, y + 12), str(val), font=text_font, fill=color)
                current_x += col_widths[j+2]

            y += row_height

        draw.text((total_width - 200, total_height - 25), "Data: blizzard.cn", font=small_font, fill=(100, 100, 100))
        return img

    @filter.command("ow数据")
    async def query_ow_stats(self, event: AstrMessageEvent):
        '''查询OW2数据。指令：/ow数据 [英雄名] 或 [分段 职责 排序]'''
        
        message_str = getattr(event, "message_str", "") or str(getattr(event, "message", ""))
        args = message_str.split()
        
        target_hero_id = None
        target_hero_cn = ""
        
        # 1. 优先检测是否为查特定英雄
        for arg in args:
            for cn, en in self.CN_TO_HERO_ID.items():
                if arg == cn or arg == en:
                    target_hero_id = en
                    target_hero_cn = cn
                    break
            if target_hero_id: break

        if target_hero_id:
            # === 模式A: 单英雄查询 ===
            yield event.plain_result(f"🔍 正在生成 {target_hero_cn} 数据图表...")
            rows = []
            for rank_en in self.RANK_ORDER:
                data_list = self._get_api_data(rank_en, "jingji")
                if not data_list: continue
                
                hero_data = next((h for h in data_list if h['hero_id'] == target_hero_id), None)
                rank_cn = self.DISPLAY_CN_MAP.get(rank_en, rank_en)
                
                if hero_data:
                    rows.append([
                        rank_cn, target_hero_cn,
                        f"{hero_data.get('win_ratio', 0)}%",
                        f"{hero_data.get('selection_ratio', 0)}%",
                        f"{hero_data.get('ban_ratio', 0)}%",
                        f"{hero_data.get('kda', 0)}",
                        target_hero_id
                    ])
                else:
                    rows.append([rank_cn, target_hero_cn, "-", "-", "-", "-", target_hero_id])

            if not rows:
                yield event.plain_result("⚠️ 未找到数据，该英雄可能被Ban或暂无数据。")
                return

            col_widths = [100, 220, 120, 100, 100, 80]
            img = self._draw_table(f"守望先锋国服 S{self.CURRENT_SEASON} {target_hero_cn} 数据趋势", 
                                   ["段位", "英雄", "胜率", "出场", "禁用", "KDA"], rows, col_widths)
            
            bio = BytesIO()
            img.save(bio, format='PNG')
            yield event.chain_result([AstrImage.fromBytes(bio.getvalue())])

        else:
            # === 模式B: 排行榜查询 ===
            game_mode = "jingji"
            rank_code = -127
            role_code = "0"
            sort_key = "win_ratio"
            
            for arg in args:
                arg_l = arg.lower()
                # 模糊匹配模式词
                if any(k in arg for k in ["快速", "休闲", "匹配", "娱乐"]):
                    game_mode = "kuaisu"
                elif any(k in arg for k in ["竞技", "排位", "天梯", "上分"]):
                    game_mode = "jingji"
                # 匹配参数
                elif arg in self.RANK_MAP:
                    rank_code = self.RANK_MAP[arg]
                elif arg in self.ROLE_MAP:
                    role_code = self.ROLE_MAP[arg]
                # 匹配排序
                elif "出场" in arg or "选取" in arg or "热度" in arg: 
                    sort_key = "selection_ratio"
                elif "胜" in arg: 
                    sort_key = "win_ratio"
                elif "禁" in arg or "ban" in arg_l: 
                    sort_key = "ban_ratio"
                elif "kda" in arg_l: 
                    sort_key = "kda"

            # 映射回标准中文名 (用于标题)
            rank_cn = self.DISPLAY_CN_MAP.get(rank_code, "未知分段")
            role_cn = self.DISPLAY_CN_MAP.get(str(role_code), "未知职责")
            sort_cn = self.DISPLAY_CN_MAP.get(sort_key, "未知")

            # 标题生成逻辑
            title_parts = [f"守望先锋国服 S{self.CURRENT_SEASON}"]
            
            if game_mode == "kuaisu":
                title_parts.append("快速模式")
                if rank_code != -127: title_parts.append(rank_cn)
                if role_code != "0": title_parts.append(role_cn)
            else:
                title_parts.append(rank_cn)
                title_parts.append(role_cn)
            
            title_parts.append(sort_cn)
            title = " ".join(title_parts)

            yield event.plain_result(f"🔍 正在生成 {title}...")
            
            data_list = self._get_api_data(rank_code, game_mode)
            if not data_list:
                yield event.plain_result(f"⚠️ {rank_cn} 暂无数据。")
                return

            filtered = [h for h in data_list if role_code == "0" or str(h.get("hero_type")) == str(role_code)]
            filtered.sort(key=lambda x: float(x.get(sort_key, 0)), reverse=True)
            
            rows = []
            for i, h in enumerate(filtered[:20]):
                en_id = h.get("hero_id", "").lower()
                cn_name = self.HERO_NAME_MAP.get(en_id, en_id)
                
                # 快速模式不显示禁用率
                if game_mode == "kuaisu":
                    cols = [
                        f"{i+1}", cn_name,
                        f"{h.get('win_ratio', 0)}%",
                        f"{h.get('selection_ratio', 0)}%",
                        f"{h.get('kda', 0)}",
                        en_id
                    ]
                else:
                    cols = [
                        f"{i+1}", cn_name,
                        f"{h.get('win_ratio', 0)}%",
                        f"{h.get('selection_ratio', 0)}%",
                        f"{h.get('ban_ratio', 0)}%",
                        f"{h.get('kda', 0)}",
                        en_id
                    ]
                rows.append(cols)

            if game_mode == "kuaisu":
                col_widths = [60, 240, 130, 110, 80] 
                # === 修复点：将 "#" 改为 ""，左上角不再显示井号 ===
                headers = ["", "英雄", "胜率", "出场", "KDA"]
            else:
                col_widths = [60, 240, 130, 110, 110, 80]
                # === 修复点：将 "#" 改为 ""，左上角不再显示井号 ===
                headers = ["", "英雄", "胜率", "出场", "禁用", "KDA"]

            img = self._draw_table(title, headers, rows, col_widths)
            
            bio = BytesIO()
            img.save(bio, format='PNG')
            yield event.chain_result([AstrImage.fromBytes(bio.getvalue())])
