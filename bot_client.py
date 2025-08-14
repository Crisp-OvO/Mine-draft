# bot_client.py
import json
import uuid
from typing import Any, Dict, Optional

import requests

from config import get_api_config, get_headers, SYSTEM_PROMPT, SESSION_ID


class BotClient:
    def __init__(self) -> None:
        self.api = get_api_config()
        self.headers = get_headers()
        self.session_id = SESSION_ID or str(uuid.uuid4())

    def _is_coze_v1(self) -> bool:
        host = self.api.base_url.lower()
        return "coze.cn" in host and "/v1" in host or host.endswith("coze.cn")

    def _is_dashscope_compatible(self) -> bool:
        host = self.api.base_url.lower()
        return "dashscope.aliyuncs.com" in host and "compatible-mode" in host

    def _build_payload(self, prompt_with_memory: str) -> Dict[str, Any]:
        if self._is_coze_v1():
            # Coze v1 chat.completions 兼容：使用 bot_id + query
            return {
                "bot_id": self.api.agent_id,
                "user": self.session_id,
                "query": prompt_with_memory,
                "stream": False,
            }

        if self.api.api_mode == "agent":
            # 通用“调用已发布智能体”接口示例
            return {
                "agent_id": self.api.agent_id,
                "input": prompt_with_memory,
                "session_id": self.session_id,
                "system": SYSTEM_PROMPT,
            }
        # OpenAI 兼容接口（chat.completions）
        return {
            "model": self.api.agent_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_with_memory},
            ],
            "temperature": 0.3,
            "stream": False,
            "user": self.session_id,
        }

    def _resolve_url(self) -> str:
        base = self.api.base_url.rstrip("/")
        if self._is_coze_v1():
            if base.endswith("/v1"):
                return f"{base}/chat/completions"
            return f"{base}/v1/chat/completions"
        if self._is_dashscope_compatible():
            # DashScope OpenAI 兼容模式固定路径
            if base.endswith("/v1"):
                return f"{base}/chat/completions"
            # 允许 base = https://dashscope.aliyuncs.com/compatible-mode
            return f"{base}/v1/chat/completions"
        if self.api.api_mode == "agent":
            return f"{base}/v1/agents/{self.api.agent_id}/invoke"
        return f"{base}/v1/chat/completions"

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=self.api.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code if e.response else ''}", "detail": str(e), "text": getattr(e.response, 'text', '')}
        except Exception as e:
            return {"error": "NETWORK/UNKNOWN", "detail": str(e)}

    def call_bot(self, prompt_with_memory: str) -> Optional[Dict[str, Any]]:
        payload = self._build_payload(prompt_with_memory)
        url = self._resolve_url()
        result = self._post(url, payload)
        return result
