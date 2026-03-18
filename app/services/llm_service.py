import httpx

from app.core.config import settings

DOMAIN_SYSTEM_PROMPTS: dict[str, str] = {
    "medical": (
        "당신은 의학 전문 RAG 어시스턴트입니다.\n"
        "반드시 제공된 의학 문헌과 문맥에 근거해서만 답변하세요.\n"
        "진단, 처방, 치료 결정을 단정짓지 말고, 항상 '전문의와 상담하세요' 안전장치를 포함하세요.\n"
        "의학 용어를 정확히 사용하되, 이해하기 어려운 용어는 간략히 설명하세요.\n"
        "근거가 부족하면 '확인 필요 — 전문의 상담을 권장합니다'라고 답하세요.\n"
        "답변은 한국어로 작성하세요."
    ),
    "english": (
        "You are a high school English education RAG assistant.\n"
        "Answer only based on the provided educational materials and context.\n"
        "Use clear, student-friendly language appropriate for high school level.\n"
        "When explaining grammar or vocabulary, provide concise examples.\n"
        "If the context is insufficient, say '자료가 부족합니다. 교재를 추가로 등록해 주세요.'\n"
        "Respond in Korean when the question is in Korean, otherwise respond in English."
    ),
    "general": (
        "당신은 도메인 특화 RAG 어시스턴트입니다.\n"
        "반드시 제공된 문맥에 근거해서만 답변하세요.\n"
        "근거가 부족하면 추정하지 말고 '확인 필요'라고 답하세요.\n"
        "답변은 한국어로 작성하세요."
    ),
}


class LLMService:
    def __init__(self):
        self.base_url = settings.vllm_base_url.rstrip("/")
        self.model = settings.vllm_model
        self.api_key = settings.vllm_api_key

    def generate_answer(self, question: str, chunks: list[dict], domain: str = "general") -> str:
        if not chunks:
            return "관련 문서를 찾지 못했습니다. 문서를 먼저 등록하거나 질문을 더 구체적으로 입력해 주세요."

        context = "\n\n".join(
            [
                f"[문서 {i}] 제목: {chunk['title']}\n내용: {chunk['content']}"
                for i, chunk in enumerate(chunks, start=1)
            ]
        )

        system_prompt = DOMAIN_SYSTEM_PROMPTS.get(domain, DOMAIN_SYSTEM_PROMPTS["general"])

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
