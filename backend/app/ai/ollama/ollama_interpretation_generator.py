import json
from urllib import error, request

from app.ai.interpretation_generator import InterpretationGenerator
from app.ai.prompt_loader import load_prompt
from app.ai.validators.report_llm_output_validator import validate_and_convert_report_llm_output
from app.schemas.feature import InputFeature
from app.schemas.history_context import PersonalHistoryContext
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.knowledge_context import AestheticKnowledgeContext
from app.schemas.report import Insight
from app.schemas.report_llm_output import InterpretationLLMOutput


PROMPT_VERSION = "interpretations.generate.v1"


class OllamaInterpretationGenerator:
    def __init__(self, base_url: str, model_name: str, timeout_seconds: int = 120) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds
        self._system_prompt = load_prompt("interpretations.generate.v1.prompt.md")

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def generate(
        self,
        groups: list[SimilarityGroup],
        features: list[InputFeature],
        input_ids: list[str],
        history_context: PersonalHistoryContext | None = None,
        knowledge_context: AestheticKnowledgeContext | None = None,
    ) -> tuple[list[PossibleInterpretation], list[Insight]]:
        user_payload = {
            "inputIds": input_ids,
            "similarityGroups": [group.model_dump(by_alias=True) for group in groups],
            "features": [
                feature.model_dump(by_alias=True)
                for feature in features
                if feature.input_id in input_ids
            ],
            "historyContext": history_context.model_dump(by_alias=True) if history_context else None,
            "knowledgeContext": knowledge_context.model_dump(by_alias=True) if knowledge_context else None,
        }
        user_message = (
            "Generate interpretations and insights for this analysis job. "
            "Return JSON only.\n\n"
            f"{json.dumps(user_payload, ensure_ascii=False)}"
        )
        raw = self._chat_json(user_message)
        payload = InterpretationLLMOutput.model_validate(raw)
        payload = payload.model_copy(update={"modelName": self._model_name, "promptVersion": PROMPT_VERSION})
        return validate_and_convert_report_llm_output(payload, input_ids, PROMPT_VERSION)

    def _chat_json(self, user_message: str) -> dict[str, object]:
        payload = json.dumps(
            {
                "model": self._model_name,
                "messages": [
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "format": "json",
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"Ollama chat request failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise ValueError(f"Ollama chat request failed: {exc.reason}") from exc

        message = body.get("message") or {}
        content = message.get("content")
        if not content:
            raise ValueError("Ollama chat response missing message content")
        if isinstance(content, dict):
            return content
        return json.loads(str(content))


def as_interpretation_generator(generator: OllamaInterpretationGenerator) -> InterpretationGenerator:
    return generator
