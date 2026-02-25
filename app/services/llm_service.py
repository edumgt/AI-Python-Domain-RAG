import httpx

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.base_url = settings.vllm_base_url.rstrip("/")
        self.model = settings.vllm_model
        self.api_key = settings.vllm_api_key

    def generate_answer(self, question: str, chunks: list[dict]) -> str:
        if not chunks:
            return "관련 문서를 찾지 못했습니다. 문서를 먼저 등록하거나 질문을 더 구체적으로 입력해 주세요."

        context = "\n\n".join(
            [
                f"[문서 {i}] 제목: {chunk['title']}\n내용: {chunk['content']}"
                for i, chunk in enumerate(chunks, start=1)
            ]
        )

        system_prompt = (
            "당신은 도메인 특화 RAG 어시스턴트입니다.\n"
            "반드시 제공된 문맥에 근거해서만 답변하세요.\n"
            "근거가 부족하면 추정하지 말고 '확인 필요'라고 답하세요.\n"
            "답변은 한국어로 작성하세요."
        )

        user_prompt = (
            f"질문:\n{question}\n\n"
            f"참고 문맥:\n{context}\n\n"
            "위 문맥만 근거로 답변하고, 마지막에 핵심 참고 문서 제목을 짧게 언급하세요."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 700,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            titles = ", ".join(sorted(set(chunk["title"] for chunk in chunks)))
            return (
                f"LLM 호출에 실패했습니다: {e}\n\n"
                f"대신 검색 결과 기준으로 보면, 관련 문서는 {titles} 입니다."
            )
