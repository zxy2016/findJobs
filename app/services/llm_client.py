import httpx
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

from app.core.config import settings

class LLMClient(ABC):
    """抽象 LLM 客户端基类"""

    @abstractmethod
    async def analyze(self, content: str) -> Dict[str, Any]:
        """使用 LLM 分析文本内容"""
        pass

class GeminiClient(LLMClient):
    """Google Gemini API 客户端 (简化版用于调试)"""

    def __init__(self, api_key: str, model_name: str, base_url: str):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/v1/models/{self.model_name}:generateContent?key={self.api_key}"
        print(f"GeminiClient initialized for model {self.model_name}")

    async def analyze(self, content: str) -> Dict[str, Any]:
        headers = {
            'Content-Type': 'application/json',
        }
        
        # 简化 prompt 字符串，避免潜在的特殊字符问题
        prompt = (
            "请从以下简历文本中，提取关键信息并以JSON格式返回。"
            "确保返回的是一个合法的JSON对象，不要在JSON前后添加任何额外的标记，比如 ```json ... ```。"
            "需要提取的字段包括：姓名(name), 电话(phone), 邮箱(email), "
            "技能(skills), 工作经验(work_experience), 教育背景(education)。"
            "\n\n简历文本如下：\n---\n"
            f"{content}\n---"
        )

        json_data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=json_data, timeout=120.0)
                response.raise_for_status()
                
                # 打印原始响应用于调试
                raw_response_json = response.json()
                print(f"--- DEBUG: Raw Gemini API Response JSON ---\n{json.dumps(raw_response_json, indent=2, ensure_ascii=False)}\n---------------------------------")

                # 1. 先解析最外层 JSON，提取 text 字段
                text_content = raw_response_json['candidates'][0]['content']['parts'][0]['text']

                # 2. 处理 text 字段中可能包含的 markdown 标记
                if '```json' in text_content:
                    json_str = text_content.split('```json')[1].split('```')[0].strip()
                else:
                    json_str = text_content
                
                # 3. 解析最终的 JSON 字符串
                return json.loads(json_str)

        except (httpx.HTTPStatusError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"调用或解析 Gemini API 失败: {e}")
            # 在生产环境中，这里应该使用更完善的日志记录
            raise
        except Exception as e:
            print(f"调用 Gemini API 时发生未知错误: {e}")
            raise

class GenericLLMClient(LLMClient):
    """一个备用客户端，用于指示配置错误。"""
    async def analyze(self, content: str) -> Dict[str, Any]:
        print("警告: 正在使用通用的 LLM 客户端，这通常表示配置不正确。")
        raise NotImplementedError("没有配置特定的 LLM 服务商 (例如在 .env 文件中设置 LLM_PROVIDER=google)")

def get_llm_client() -> LLMClient:
    """
    LLM 客户端工厂函数。
    根据配置返回一个 LLM 客户端实例。
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "google":
        if not all([settings.LLM_API_KEY, settings.LLM_MODEL_NAME, settings.LLM_API_BASE_URL]):
            raise ValueError("对于 google provider, LLM_API_KEY, LLM_MODEL_NAME, 和 LLM_API_BASE_URL 必须全部设置。")
        return GeminiClient(
            api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            base_url=settings.LLM_API_BASE_URL
        )
    
    return GenericLLMClient()