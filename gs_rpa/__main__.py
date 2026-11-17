"""Comando unificado para validar o projeto e iniciar o site local."""

from __future__ import annotations

import argparse
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


def parse_arguments() -> argparse.Namespace:
    """Lê o cenário que será usado na ocorrência automática."""

    parser = argparse.ArgumentParser(
        description="Executa os testes e inicia a demonstração do ArborGrid."
    )
    parser.add_argument(
        "--cenario",
        choices=("sucesso", "timeout", "erro"),
        default="sucesso",
        help="resultado da ocorrência automática (padrão: sucesso)",
    )
    return parser.parse_args()


def main() -> None:
    """Testa o projeto e inicia o site quando não há falhas."""

    arguments = parse_arguments()
    print("Executando testes do ArborGrid...")
    if not run_tests():
        raise SystemExit("Os testes falharam. O site não foi iniciado.")

    print("Testes aprovados. Iniciando o site...")
    run_server(
        initial_occurrence={
            "id": f"demo-{arguments.cenario}",
            "localizacao": "Avenida Paulista, 1000 - São Paulo",
            "fotos": ["arvore-rede-eletrica.jpg"],
            "motivo_risco": "Galhos em conflito com a rede elétrica de média tensão.",
            "modo_simulacao": arguments.cenario,
        }
    )


if __name__ == "__main__":
    main()
