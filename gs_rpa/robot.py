from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Protocol


@dataclass(frozen=True)
class ProtocolResult:
    occurrence_id: str
    status: str
    protocolo: str | None
    mensagem: str
    timestamp: str


class OccurrenceQueue(Protocol):
    def get_validated_occurrences(self) -> Iterable[Mapping[str, object]]:
        """Return validated critical-risk occurrences from the MVP queue."""


class FormClient(Protocol):
    def submit_occurrence(self, occurrence: Mapping[str, object]) -> str:
        """Submit occurrence to the city maintenance form and return protocol number."""


class StatusRepository(Protocol):
    def save_status(self, result: ProtocolResult) -> None:
        """Persist protocol status and logs in MVP database."""


class RobotZeladoria:
    def __init__(
        self,
        queue: OccurrenceQueue,
        form_client: FormClient,
        status_repository: StatusRepository,
    ) -> None:
        self._queue = queue
        self._form_client = form_client
        self._status_repository = status_repository

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def process_occurrence(self, occurrence: Mapping[str, object]) -> ProtocolResult:
        occurrence_id = str(occurrence.get("id", ""))
        try:
            protocolo = self._form_client.submit_occurrence(occurrence)
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="SUCESSO",
                protocolo=protocolo,
                mensagem="Ocorrência enviada para o formulário de zeladoria.",
                timestamp=self._timestamp(),
            )
        except TimeoutError:
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="ERRO_TIMEOUT",
                protocolo=None,
                mensagem="Timeout ao acessar ou enviar formulário de zeladoria.",
                timestamp=self._timestamp(),
            )
        except Exception as exc:
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="ERRO",
                protocolo=None,
                mensagem=f"Falha ao processar ocorrência: {exc}",
                timestamp=self._timestamp(),
            )

        self._status_repository.save_status(result)
        return result

    def run(self) -> list[ProtocolResult]:
        results: list[ProtocolResult] = []
        for occurrence in self._queue.get_validated_occurrences():
            results.append(self.process_occurrence(occurrence))
        return results
