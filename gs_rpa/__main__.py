"""Comando unificado para validar o projeto e iniciar o site local."""

from __future__ import annotations

import unittest
from pathlib import Path

from .web_app import run_server


def run_tests() -> bool:
    """Executa a suíte de testes antes de iniciar o servidor."""

    # O diretório é calculado a partir deste arquivo para funcionar em qualquer pasta atual.
    project_root = Path(__file__).resolve().parent.parent
    test_suite = unittest.defaultTestLoader.discover(
        str(project_root / "tests"),
        pattern="test_*.py",
    )
    test_result = unittest.TextTestRunner(verbosity=1).run(test_suite)
    return test_result.wasSuccessful()


def main() -> None:
    """Testa o projeto e inicia o site quando não há falhas."""

    print("Executando testes do ArborGrid...")
    if not run_tests():
        raise SystemExit("Os testes falharam. O site não foi iniciado.")

    print("Testes aprovados. Iniciando o site...")
    run_server(
        initial_occurrence={
            "id": "demo-automatico",
            "localizacao": "Avenida Paulista, 1000 - São Paulo",
            "fotos": ["arvore-rede-eletrica.jpg"],
            "motivo_risco": "Galhos em conflito com a rede elétrica de média tensão.",
            "modo_simulacao": "sucesso",
        }
    )


if __name__ == "__main__":
    main()
