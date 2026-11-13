"""Servidor web local para demonstrar o fluxo do robô de zeladoria."""

from __future__ import annotations

import json
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .mvp_db import SQLiteStatusRepository
from .robot import FormClient, RobotZeladoria


class SimulatedFormClient(FormClient):
    """Representa o portal SP156 sem depender de internet ou credenciais reais."""

    def submit_occurrence(self, occurrence: dict[str, object]) -> str:
        """Valida os campos e gera um protocolo visualmente semelhante ao portal."""

        # Estas validações representam os campos obrigatórios do portal municipal.
        if not occurrence.get("localizacao"):
            raise ValueError("Informe a localização.")
        if not occurrence.get("fotos"):
            raise ValueError("Informe ao menos uma foto.")
        if not occurrence.get("motivo_risco"):
            raise ValueError("Informe o motivo de risco.")

        # Os cenários abaixo permitem demonstrar na tela como o robô trata falhas.
        if occurrence.get("modo_simulacao") == "timeout":
            raise TimeoutError("O portal simulado demorou para responder.")
        if occurrence.get("modo_simulacao") == "erro":
            raise RuntimeError("O portal simulado está indisponível.")

        # Um identificador aleatório evita repetir protocolos entre execuções.
        return f"SP156-SIM-{uuid.uuid4().hex[:8].upper()}"


class WebOccurrenceQueue:
    """Fila mínima usada para executar uma ocorrência enviada pela interface."""

    def __init__(self, occurrence: dict[str, object]) -> None:
        # A interface envia uma ocorrência por vez para a fila de demonstração.
        self._occurrence = occurrence

    def get_validated_occurrences(self) -> list[dict[str, object]]:
        """Devolve a ocorrência já preenchida e validada pela interface."""

        return [self._occurrence]


class DemoApplication:
    """Agrupa as dependências do robô e os recursos do servidor web."""

    def __init__(self, database_path: str | Path) -> None:
        # As mesmas dependências do robô real são montadas uma única vez.
        self.repository = SQLiteStatusRepository(database_path)
        self.form_client = SimulatedFormClient()

    def process(self, occurrence: dict[str, object]):
        """Executa o mesmo fluxo de produção usado pelo robô."""

        # A aplicação conecta a fila web, o portal simulado e o banco ao robô.
        robot = RobotZeladoria(
            WebOccurrenceQueue(occurrence),
            self.form_client,
            self.repository,
        )
        return robot.run()[0]

    def history(self):
        """Lê o histórico persistido para exibição na tela."""

        return self.repository.list_statuses()


def _result_to_dict(result: Any) -> dict[str, object]:
    """Converte um resultado do robô para o formato JSON da API."""

    # O formato JSON usa os mesmos campos do ProtocolResult.
    return {
        "occurrence_id": result.occurrence_id,
        "status": result.status,
        "protocolo": result.protocolo,
        "mensagem": result.mensagem,
        "timestamp": result.timestamp,
    }


def create_handler(application: DemoApplication, static_directory: Path):
    """Cria um handler com acesso à aplicação e aos arquivos da interface."""

    class ApplicationHandler(BaseHTTPRequestHandler):
        """Atende a página e os endpoints JSON da demonstração."""

        def _send_json(self, payload: object, status: int = 200) -> None:
            """Envia uma resposta JSON com cabeçalhos apropriados."""

            # Serializa em UTF-8 para preservar mensagens em português.
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path) -> None:
            """Entrega um arquivo estático da interface web."""

            # Impede que uma requisição tente acessar arquivos fora da pasta web.
            if not path.is_file() or static_directory not in path.parents:
                self.send_error(404)
                return

            body = path.read_bytes()
            content_type = "text/html; charset=utf-8" if path.suffix == ".html" else "text/plain"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            """Responde à página principal e ao histórico."""

            # A página e o histórico usam o mesmo servidor, mas rotas diferentes.
            route = urlparse(self.path).path
            if route == "/api/history":
                self._send_json([_result_to_dict(item) for item in application.history()])
                return
            if route in {"/", "/index.html"}:
                self._send_file(static_directory / "index.html")
                return
            self.send_error(404)

        def do_POST(self) -> None:
            """Recebe uma ocorrência e executa o robô."""

            # Apenas a rota de processamento aceita dados enviados pelo formulário.
            if urlparse(self.path).path != "/api/process":
                self.send_error(404)
                return

            try:
                # Lê o JSON enviado pelo navegador e normaliza os campos textuais.
                size = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(size))
                foto = str(payload.get("foto", "")).strip()
                occurrence = {
                    "id": str(payload.get("id") or f"web-{uuid.uuid4().hex[:8]}"),
                    "localizacao": str(payload.get("localizacao", "")).strip(),
                    "fotos": [foto] if foto else [],
                    "motivo_risco": str(payload.get("motivo_risco", "")).strip(),
                    "modo_simulacao": payload.get("modo_simulacao", "sucesso"),
                }
                # O resultado passa pelo fluxo RobotZeladoria antes de voltar ao navegador.
                result = application.process(occurrence)
                self._send_json(_result_to_dict(result))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                self._send_json({"erro": f"Dados inválidos: {exc}"}, status=400)

        def log_message(self, format: str, *args: object) -> None:
            """Mantém o terminal limpo; o histórico fica disponível na interface."""

    return ApplicationHandler


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Inicia o servidor local e mantém o processo atendendo requisições."""

    # Os caminhos são calculados a partir da raiz do projeto, não do terminal atual.
    root = Path(__file__).resolve().parent.parent
    application = DemoApplication(root / "rpa_demo.sqlite3")
    static_directory = root / "web"
    server = ThreadingHTTPServer((host, port), create_handler(application, static_directory))
    print(f"ArborGrid RPA disponível em http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
