# GS-RPA

Automação em Python para consumir ocorrências de árvores de risco crítico validadas no MVP e registrar protocolos de atendimento da zeladoria.

## Fluxo ponta a ponta

1. Lê a fila de ocorrências validadas.
2. Acessa o formulário de zeladoria (simulando portal SP156) via `FormClient`.
3. Preenche dados da ocorrência (localização, fotos e motivo de risco) no cliente de formulário.
4. Extrai o número de protocolo retornado e grava status/log no banco do MVP (`StatusRepository`).
5. Em caso de timeout, grava `ERRO_TIMEOUT`; em outros erros, grava `ERRO`.

## Estrutura

- `/home/runner/work/GS-RPA/GS-RPA/gs_rpa/robot.py`: fluxo principal do robô.
- `/home/runner/work/GS-RPA/GS-RPA/gs_rpa/mvp_db.py`: repositório SQLite para persistência de status e logs.
- `/home/runner/work/GS-RPA/GS-RPA/tests/test_robot.py`: testes unitários focados no fluxo e tratamento de erros.

## Testes

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
