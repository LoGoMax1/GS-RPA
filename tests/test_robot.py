import unittest

from gs_rpa.robot import ProtocolResult, RobotZeladoria


class FakeQueue:
    def __init__(self, occurrences):
        self._occurrences = occurrences

    def get_validated_occurrences(self):
        return self._occurrences


class FakeFormClient:
    def __init__(self, protocol_number=None, error=None):
        self.protocol_number = protocol_number
        self.error = error

    def submit_occurrence(self, occurrence):
        if self.error:
            raise self.error
        if not occurrence.get("localizacao") or not occurrence.get("fotos") or not occurrence.get("motivo_risco"):
            raise ValueError("Campos obrigatórios ausentes")
        return self.protocol_number or "PROTOCOLO-DEFAULT"


class MemoryRepository:
    def __init__(self):
        self.saved = []

    def save_status(self, result: ProtocolResult):
        self.saved.append(result)


class RobotZeladoriaTests(unittest.TestCase):
    def test_run_processes_validated_queue_and_logs_success(self):
        occurrence = {
            "id": "occ-1",
            "localizacao": "Rua A, 100",
            "fotos": ["foto1.jpg"],
            "motivo_risco": "Árvore com risco de queda",
        }
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(protocol_number="SP156-123"), repository)

        results = robot.run()

        self.assertEqual(1, len(results))
        self.assertEqual("SUCESSO", results[0].status)
        self.assertEqual("SP156-123", results[0].protocolo)
        self.assertEqual(1, len(repository.saved))

    def test_timeout_is_captured_and_logged(self):
        occurrence = {
            "id": "occ-2",
            "localizacao": "Rua B, 200",
            "fotos": ["foto2.jpg"],
            "motivo_risco": "Galhos sobre rede elétrica",
        }
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(error=TimeoutError("timeout de página")), repository)

        result = robot.run()[0]

        self.assertEqual("ERRO_TIMEOUT", result.status)
        self.assertIsNone(result.protocolo)
        self.assertIn("Timeout", result.mensagem)
        self.assertEqual(1, len(repository.saved))

    def test_unexpected_error_is_captured_and_logged(self):
        occurrence = {
            "id": "occ-3",
            "localizacao": "Rua C, 300",
            "fotos": ["foto3.jpg"],
            "motivo_risco": "Inclinação acentuada",
        }
        queue = FakeQueue([occurrence])
        repository = MemoryRepository()
        robot = RobotZeladoria(queue, FakeFormClient(error=RuntimeError("portal indisponível")), repository)

        result = robot.run()[0]

        self.assertEqual("ERRO", result.status)
        self.assertIsNone(result.protocolo)
        self.assertIn("portal indisponível", result.mensagem)
        self.assertEqual(1, len(repository.saved))


if __name__ == "__main__":
    unittest.main()
