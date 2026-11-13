# GS-RPA · ArborGrid

Automação em Python para consumir ocorrências de árvores de risco crítico validadas no MVP, simular o envio ao portal SP156 e registrar protocolos de atendimento da zeladoria.

> Este projeto contém um MVP demonstrável localmente. O portal da Prefeitura é simulado; nenhum chamado real é aberto.

## Integrantes

| Registro | Nome |
|---|---|
| 551117 | Lorenzo Gomes Andreata |
| 97158 | Lucas Moreno Matheus |
| 99756 | Kayky Oliveira Schunck |

## Fluxo ponta a ponta

1. Lê a fila de ocorrências validadas.
2. Preenche localização, foto e motivo de risco no formulário simulado.
3. Extrai o número de protocolo gerado pelo portal simulado.
4. Grava o status e o log no banco SQLite do MVP.
5. Em caso de timeout, grava `ERRO_TIMEOUT`; em outros erros, grava `ERRO`.

## Estrutura

- `gs_rpa/robot.py`: contratos e fluxo principal do robô.
- `gs_rpa/mvp_db.py`: persistência de status e logs em SQLite.
- `gs_rpa/web_app.py`: servidor local, API e portal SP156 simulado.
- `web/index.html`: interface visual para executar o robô.
- `tests/test_robot.py`: testes unitários do fluxo e tratamento de erros.

## Testes

Execute a suíte com:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Site local de demonstração

O site permite acompanhar o processo de forma visual, sem instalar dependências externas, usar credenciais ou acessar um portal real.

### Iniciar

```bash
python -m gs_rpa.web_app
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador, preencha a ocorrência e clique em **Executar robô**.

O campo **Foto ou evidência** aceita arquivos de imagem (`.jpg`, `.jpeg`, `.png` etc.) e mostra uma prévia antes do envio. Como o portal é simulado, o MVP registra o nome do arquivo, sem fazer upload para um serviço externo.

### Cenários disponíveis

- **Sucesso:** gera um protocolo como `SP156-SIM-XXXXXXXX`.
- **Timeout:** demonstra o status `ERRO_TIMEOUT`.
- **Erro:** demonstra o status `ERRO` quando o portal está indisponível.

Cada execução aparece no histórico da tela e é salva no arquivo local `rpa_demo.sqlite3`, que é ignorado pelo Git.

### Arquitetura simplificada

```text
Formulário web
      ↓
API local (/api/process)
      ↓
RobotZeladoria
      ↓
Portal SP156 simulado
      ↓
SQLite + histórico na tela
```
