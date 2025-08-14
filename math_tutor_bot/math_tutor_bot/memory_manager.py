# memory_manager.py
import json
import os
import uuid
from typing import Any, Dict

from config import MEMORY_FILE_PATH, SESSION_ID


class MemoryManager:
    def __init__(self) -> None:
        self.file_path = MEMORY_FILE_PATH
        self._ensure_file()
        self.session_id = SESSION_ID or str(uuid.uuid4())

    def _ensure_file(self) -> None:
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": None,
                    "progress": [],
                    "weak_points": [],
                    "error_patterns": [],
                }, f, ensure_ascii=False, indent=2)

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("session_id", self.session_id)
        data.setdefault("progress", [])
        data.setdefault("weak_points", [])
        data.setdefault("error_patterns", [])
        return data

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_memory_context(self) -> Dict[str, Any]:
        data = self._load()
        # 暴露给 prompt 的结构（与模板里占位一致）
        return {
            "session_id": data.get("session_id", self.session_id),
            "progress": data.get("progress", []),
            "weak_points": data.get("weak_points", []),
            "error_patterns": data.get("error_patterns", []),
        }

    def update_memory(self, bot_response: Dict[str, Any]) -> None:
        data = self._load()
        # 这里根据你的平台返回结构进行抽取；以下是通用示例
        text = None
        # 常见返回结构 1：{"data": {"content": "..."}}
        if isinstance(bot_response, dict):
            text = bot_response.get("data", {}).get("content")
            if not text:
                # 常见返回结构 2：OpenAI 格式
                choices = bot_response.get("choices")
                if isinstance(choices, list) and choices:
                    message = choices[0].get("message") or {}
                    text = message.get("content")

        if not text:
            # 若无法解析内容，不更新
            return

        # 简单启发式：
        # - 若包含“进步/正确/太棒”等，加入 progress
        # - 若包含“错误/修复/注意”等，加入 error_patterns
        lowered = str(text).lower()
        if any(k in lowered for k in ["正确", "太棒", "进步", "成功", "做得好"]):
            data.setdefault("progress", []).append("表现有提升或被表扬")
        if any(k in lowered for k in ["错误", "修复", "注意", "警报", "改正"]):
            data.setdefault("error_patterns", []).append("曾出现关键步骤错误")
        # 弱项：根据关键词
        if any(k in lowered for k in ["移项", "分数", "括号", "符号"]):
            data.setdefault("weak_points", []).append("需巩固：移项/分数/括号/符号")

        data["session_id"] = self.session_id
        self._save(data)
