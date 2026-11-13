# Permite usar anotações de tipo modernas sem avaliá-las imediatamente.
from __future__ import annotations

# Dataclass gera automaticamente métodos como __init__ e __repr__.
from dataclasses import dataclass
# datetime e timezone são usados para registrar quando cada ocorrência foi processada.
from datetime import datetime, timezone
# Esses tipos descrevem as interfaces que o robô espera receber.
from typing import Iterable, Mapping, Protocol


@dataclass(frozen=True)
class ProtocolResult:
    """Representa o resultado do envio de uma ocorrência ao formulário."""

    # Identificador da ocorrência que foi processada.
    occurrence_id: str
    # Situação final do processamento, como SUCESSO ou ERRO_TIMEOUT.
    status: str
    # Número de protocolo retornado pelo formulário, quando o envio funciona.
    protocolo: str | None
    # Mensagem explicando o resultado do processamento.
    mensagem: str
    # Data e hora do resultado no formato ISO 8601, em UTC.
    timestamp: str


class OccurrenceQueue(Protocol):
    """Define a fonte de ocorrências validadas que o robô deve processar."""

    def get_validated_occurrences(self) -> Iterable[Mapping[str, object]]:
        """Retorna as ocorrências críticas validadas pela fila do MVP."""


class FormClient(Protocol):
    """Define o cliente responsável por enviar uma ocorrência ao formulário."""

    def submit_occurrence(self, occurrence: Mapping[str, object]) -> str:
        """Envia a ocorrência ao formulário e retorna o número do protocolo."""


class StatusRepository(Protocol):
    """Define o armazenamento dos resultados e logs do processamento."""

    def save_status(self, result: ProtocolResult) -> None:
        """Persiste o status e os logs no banco do MVP."""


class RobotZeladoria:
    """Orquestra a leitura, o envio e o registro das ocorrências."""

    def __init__(
        self,
        queue: OccurrenceQueue,
        form_client: FormClient,
        status_repository: StatusRepository,
    ) -> None:
        # A fila fornece ocorrências, o cliente envia os dados e o repositório salva os resultados.
        self._queue = queue
        self._form_client = form_client
        self._status_repository = status_repository

    @staticmethod
    def _timestamp() -> str:
        """Retorna o horário atual em UTC no formato ISO 8601."""

        return datetime.now(timezone.utc).isoformat()

    def process_occurrence(self, occurrence: Mapping[str, object]) -> ProtocolResult:
        """Envia uma ocorrência, transforma o resultado em status e salva esse status."""

        # Converte o identificador para texto e usa texto vazio quando ele não existe.
        occurrence_id = str(occurrence.get("id", ""))
        try:
            # O cliente pode retornar o número de protocolo ou lançar um erro.
            protocolo = self._form_client.submit_occurrence(occurrence)
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="SUCESSO",
                protocolo=protocolo,
                mensagem="Ocorrência enviada para o formulário de zeladoria.",
                timestamp=self._timestamp(),
            )
        except TimeoutError:
            # Timeout recebe um status específico para facilitar o monitoramento.
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="ERRO_TIMEOUT",
                protocolo=None,
                mensagem="Timeout ao acessar ou enviar formulário de zeladoria.",
                timestamp=self._timestamp(),
            )
        except Exception as exc:
            # Outros erros são registrados com a mensagem original para diagnóstico.
            result = ProtocolResult(
                occurrence_id=occurrence_id,
                status="ERRO",
                protocolo=None,
                mensagem=f"Falha ao processar ocorrência: {exc}",
                timestamp=self._timestamp(),
            )

        # O resultado é persistido tanto em sucesso quanto em qualquer erro tratado.
        self._status_repository.save_status(result)
        return result

    def run(self) -> list[ProtocolResult]:
        """Processa todas as ocorrências validadas e retorna seus resultados."""

        # Mantém os resultados em memória para que o chamador possa consultá-los.
        results: list[ProtocolResult] = []
        for occurrence in self._queue.get_validated_occurrences():
            # Cada ocorrência é processada individualmente, sem interromper o fluxo por erro de envio.
            results.append(self.process_occurrence(occurrence))
        return results
