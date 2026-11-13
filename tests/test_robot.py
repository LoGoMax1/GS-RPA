# Importa o framework de testes da biblioteca padrão do Python.
import unittest

# Importa os objetos do fluxo que serão exercitados pelos testes.
from gs_rpa.robot import ProtocolResult, RobotZeladoria


class FakeQueue:
    """Fila falsa usada para fornecer ocorrências determinísticas aos testes."""

    def __init__(self, occurrences):
        # Guarda a lista que será devolvida pelo método da fila.
        self._occurrences = occurrences

    def get_validated_occurrences(self):
        """Retorna as ocorrências preparadas pelo teste."""

        return self._occurrences


class FakeFormClient:
    """Cliente falso que simula sucesso, timeout ou falha no formulário."""

    def __init__(self, protocol_number=None, error=None):
        # Permite configurar o protocolo de sucesso e um erro opcional.
        self.protocol_number = protocol_number
        self.error = error

    def submit_occurrence(self, occurrence):
        """Valida o mínimo necessário e simula o envio ao formulário."""

        # Quando configurado, o erro é lançado antes de qualquer validação.
        if self.error:
            raise self.error
        # Reproduz a exigência do formulário por dados obrigatórios.
        if not occurrence.get("localizacao") or not occurrence.get("fotos") or not occurrence.get("motivo_risco"):
            raise ValueError("Campos obrigatórios ausentes")
        # Retorna o protocolo configurado ou um valor padrão para o teste.
        return self.protocol_number or "PROTOCOLO-DEFAULT"


class MemoryRepository:
    """Repositório falso que guarda resultados apenas na memória."""

    def __init__(self):
        # A lista permite verificar se o robô salvou o resultado.
        self.saved = []

    def save_status(self, result: ProtocolResult):
        """Adiciona o resultado à lista de resultados salvos."""

        self.saved.append(result)


class RobotZeladoriaTests(unittest.TestCase):
    """Testa os principais caminhos do processamento de ocorrências."""

    def test_run_processes_validated_queue_and_logs_success(self):
        """Verifica envio bem-sucedido, protocolo retornado e persistência."""

        # Cria uma ocorrência com todos os campos exigidos pelo cliente falso.
        occurrence = {
            "id": "occ-1",
            "localizacao": "Rua A, 100",
            "fotos": ["foto1.jpg"],
            "motivo_risco": "Árvore com risco de queda",
        }
        # Monta as dependências falsas e o robô sob teste.
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(protocol_number="SP156-123"), repository)

        # Executa o fluxo completo.
        results = robot.run()

        # Confirma o resultado do envio e o registro no repositório.
        self.assertEqual(1, len(results))
        self.assertEqual("SUCESSO", results[0].status)
        self.assertEqual("SP156-123", results[0].protocolo)
        self.assertEqual(1, len(repository.saved))

    def test_timeout_is_captured_and_logged(self):
        """Verifica que timeout gera status específico e é persistido."""

        # Cria uma ocorrência válida para que a falha simulada seja um timeout.
        occurrence = {
            "id": "occ-2",
            "localizacao": "Rua B, 200",
            "fotos": ["foto2.jpg"],
            "motivo_risco": "Galhos sobre rede elétrica",
        }
        # Configura o cliente para simular timeout e o repositório em memória.
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(error=TimeoutError("timeout de página")), repository)

        # Processa a fila e obtém o único resultado.
        result = robot.run()[0]

        # Confirma o tratamento específico de timeout.
        self.assertEqual("ERRO_TIMEOUT", result.status)
        self.assertIsNone(result.protocolo)
        self.assertIn("Timeout", result.mensagem)
        self.assertEqual(1, len(repository.saved))

    def test_unexpected_error_is_captured_and_logged(self):
        """Verifica que uma falha inesperada gera ERRO e é persistida."""

        # Cria outra ocorrência válida para simular indisponibilidade do portal.
        occurrence = {
            "id": "occ-3",
            "localizacao": "Rua C, 300",
            "fotos": ["foto3.jpg"],
            "motivo_risco": "Inclinação acentuada",
        }
        # Configura o cliente para lançar uma exceção genérica.
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(error=RuntimeError("portal indisponível")), repository)

        # Processa a ocorrência e coleta o resultado gerado pelo robô.
        result = robot.run()[0]

        # Confirma o status genérico, a ausência de protocolo e a mensagem do erro.
        self.assertEqual("ERRO", result.status)
        self.assertIsNone(result.protocolo)
        self.assertIn("portal indisponível", result.mensagem)
        self.assertEqual(1, len(repository.saved))


# Permite executar este arquivo diretamente pela linha de comando.
if __name__ == "__main__":
    unittest.main()
