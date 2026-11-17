# GS-RPA · ArborGrid

Automação em Python para consumir ocorrências de árvores de risco crítico validadas no MVP, simular o envio ao portal SP156 e registrar protocolos de atendimento da zeladoria.

> Este projeto contém um MVP demonstrável localmente. O portal da Prefeitura é simulado; nenhum chamado real é aberto.

## Integrantes

| Registro | Nome |
|---|---|
| 551117 | Lorenzo Gomes Andreata |
| 97158 | Lucas Moreno Matheus |
| 99756 | Kayky Oliveira Schunck |

## Video 

https://www.youtube.com/watch?v=02Gy9LZp72g

## Problema e solução da automação

### Problema

Em São Paulo e na região metropolitana, árvores em situação de risco podem atingir a rede elétrica e causar quedas de energia, bloqueios de vias e riscos para moradores. Mesmo quando uma ocorrência é identificada e validada, o registro manual no canal de zeladoria pode ser demorado, repetitivo e sujeito a falhas.

Esse processo também dificulta o acompanhamento: sem um protocolo e um histórico organizado, fica mais difícil saber quais ocorrências foram enviadas, quais falharam e quais precisam ser processadas novamente.

### Solução

O ArborGrid automatiza a abertura e o acompanhamento dessas solicitações. O robô recebe ocorrências críticas já validadas, preenche o formulário de zeladoria, captura o protocolo e salva o resultado em um banco SQLite.

O MVP também trata situações de timeout e indisponibilidade do portal. Dessa forma, a equipe consegue visualizar o sucesso ou a falha de cada tentativa, mantendo um histórico para auditoria e acompanhamento.

O site local permite demonstrar esse processo de forma acessível, sem depender do portal real, de credenciais ou de serviços externos. Na versão atual, o portal SP156 é simulado para fins de apresentação e testes.

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
- `docs/`: fluxograma e PDD do processo.
- `logs/`: amostras sanitizadas de execuções, sem dados sensíveis.
- `assets/`: evidências visuais da arquitetura e da tela de demonstração.

### Artefatos de documentação e evidência

O repositório inclui os artefatos solicitados para a apresentação:

- [Fluxograma do RPA](docs/fluxo-rpa.md)
- [PDD — Documento de Desenho do Processo](docs/PDD.md)
- [Amostras de logs](logs/exemplo-execucao.log)
- [Evidências visuais](assets/)

## Testes

Execute a suíte com:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Site local de demonstração

O site permite acompanhar o processo de forma visual, sem instalar dependências externas, usar credenciais ou acessar um portal real.

### Iniciar

```bash
python -m gs_rpa
```

Esse comando executa os testes automaticamente, cria e processa uma ocorrência de demonstração e inicia o site somente se todos passarem. Ao abrir [http://127.0.0.1:8000](http://127.0.0.1:8000), a ocorrência automática já estará no histórico, sem necessidade de preenchimento manual.

O cenário padrão é sucesso. Para testar outros resultados diretamente pelo comando:

```bash
python -m gs_rpa --cenario timeout
python -m gs_rpa --cenario erro
```

Também é possível informar explicitamente:

```bash
python -m gs_rpa --cenario sucesso
```

Para processar outras ocorrências, você também pode preencher o formulário da página e clicar em **Executar robô**.

Para iniciar somente o servidor, sem rodar os testes antes:

```bash
python -m gs_rpa.web_app
```

O campo **Foto ou evidência** aceita arquivos de imagem (`.jpg`, `.jpeg`, `.png` etc.) e mostra uma prévia antes do envio. Como o portal é simulado, o MVP registra o nome do arquivo, sem fazer upload para um serviço externo.

### Cenários disponíveis

- **Sucesso:** gera um protocolo como `SP156-SIM-XXXXXXXX`.
- **Timeout:** demonstra o status `ERRO_TIMEOUT`.
- **Erro:** demonstra o status `ERRO` quando o portal está indisponível.

Cada execução aparece no histórico da tela, é salva no arquivo local `rpa_demo.sqlite3` e também é acrescentada em `logs/execucoes.log`, com data/hora, ocorrência, status, protocolo e mensagem. O banco SQLite é ignorado pelo Git; os logs ficam versionáveis para auditoria e demonstração.

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
