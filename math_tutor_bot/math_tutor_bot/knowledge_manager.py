# knowledge_manager.py
import json
import os
from typing import Any, Dict, List, Optional

import requests

from config import get_headers


class KnowledgeManager:
    def __init__(self) -> None:
        # 外部知识库检索配置（阿里云百炼：请在 .env 中设置 KB_SEARCH_URL、KB_ID、KB_TOP_K）
        self.kb_search_url: Optional[str] = os.getenv("KB_SEARCH_URL")
        self.kb_id: Optional[str] = os.getenv("KB_ID")
        try:
            self.kb_top_k: int = int(os.getenv("KB_TOP_K", "3"))
        except Exception:
            self.kb_top_k = 3
        # 本地多样化词典
        self.lexicon_path: str = os.getenv("LEXICON_FILE", os.path.join("env", "emoji_lexicon.json"))
        self.headers = get_headers()

    def retrieve_domain_knowledge(self, query: str) -> str:
        """检索阿里云百炼知识库，返回拼接后的文本。需在 .env 中配置 KB_SEARCH_URL/KB_ID。
        说明：不同账号/地域的知识库检索 API 路径可能不同，请按实际控制台文档配置 KB_SEARCH_URL。
        期望返回结构示例：{"documents": [{"title": "...", "content": "..."}, ...]}
        """
        if not self.kb_search_url or not self.kb_id:
            return ""
        payload = {
            "kb_id": self.kb_id,
            "query": query,
            "top_k": self.kb_top_k,
        }
        try:
            resp = requests.post(self.kb_search_url, headers=self.headers, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            docs: List[Dict[str, Any]] = data.get("documents") or data.get("data") or []
            if not isinstance(docs, list):
                return ""
            parts: List[str] = []
            for i, d in enumerate(docs[: self.kb_top_k], start=1):
                title = d.get("title") or d.get("name") or f"文档{i}"
                content = d.get("content") or d.get("text") or ""
                if content:
                    parts.append(f"【{title}】\n{content}")
            return "\n\n".join(parts)
        except Exception:
            return ""

    def load_lexicon(self) -> Dict[str, Any]:
        """加载本地表情/引导词/情感词词典，不存在则返回内置默认。"""
        if os.path.exists(self.lexicon_path):
            try:
                with open(self.lexicon_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # 默认多样化词典（精简示例）
        return {
            "emoji": {
                "blank": ["(◕‿◕✿)", "(•̀ᴗ•́)و", "🌈", "🌟", "(◕‿◕)"],
                "correct": ["(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "✨🎉", "(っ˘▽˘)っ🚀", "🏆"],
                "error": ["(•̀ᴗ•́)و", "(◍•ᴗ•◍)❤", "(•̃_•̃)", "💔", "🌧️"],
                "partial": ["(◕‿◕✿)", "(ﾉ◕ヮ◕)ﾉ", "(•̀ᴗ•́)و", "🌈", "💫"],
                "almost": ["🌟", "💫", "🎯", "✨", "🚀"],
            },
            "guidance": {
                "blank": ["小手准备", "魔法启动", "看这里", "试试看", "轻轻一试"],
                "correct": ["太惊艳了", "完美示范", "教科书级", "精彩绝伦", "稳稳拿下"],
                "error": ["小调整", "魔法修正", "重新施法", "微调一下", "换个角度"],
                "partial": ["突破在即", "最后冲刺", "终极挑战", "再补一步", "马上就好"],
                "almost": ["胜利在望", "终极魔法", "一击必中", "再推一把", "就差一步"],
                "try_again": ["再试一次好吗？", "我们再来一遍~", "换个方法再试", "不怕，继续！"],
                "final_push": ["冲刺一下！", "最后一步了！", "加把劲！", "稳住！"]
            },
            "emotion": {
                "blank": ["期待", "信心", "好奇", "兴奋"],
                "correct": ["骄傲", "惊喜", "欣慰", "陶醉"],
                "error": ["温柔", "耐心", "鼓励", "陪伴"],
                "partial": ["欣喜", "期待", "信心", "激动"],
            }
        } 