# PDD — Documento de Desenho do Processo

## 1. Objetivo

Automatizar o registro de ocorrências críticas de árvores que precisam de
atendimento da zeladoria, reduzindo preenchimento manual e mantendo o
acompanhamento de cada tentativa.

## 2. Escopo do MVP

O MVP demonstra localmente o fluxo de RPA. O portal SP156 é simulado e nenhum
chamado real é aberto.

### Incluído

- Recebimento de uma ocorrência validada.
- Localização, evidência fotográfica e motivo do risco.
- Geração de protocolo simulado.
- Tratamento de sucesso, timeout e erro inesperado.
- Registro persistente em SQLite.
- Consulta do histórico pela interface web.

### Fora do escopo atual

- Acesso autenticado ao portal real.
- Upload de imagens para serviço externo.
- Integração direta com visão computacional, Open-Meteo ou ANEEL.
- Reprocessamento automático de falhas.

## 3. Entrada

Uma ocorrência possui os seguintes campos:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `id` | Não | Identificador da ocorrência; um ID é gerado se não for informado. |
| `localizacao` | Sim | Endereço ou ponto de referência. |
| `fotos` | Sim | Nome da imagem selecionada na demonstração. |
| `motivo_risco` | Sim | Explicação do risco identificado. |
| `modo_simulacao` | Não | `sucesso`, `timeout` ou `erro`. |

## 4. Saída

Cada tentativa gera um `ProtocolResult` com:

- identificador da ocorrência;
- status (`SUCESSO`, `ERRO_TIMEOUT` ou `ERRO`);
- protocolo, quando houver;
- mensagem de diagnóstico;
- data e hora em UTC.

## 5. Persistência e auditoria

Os resultados são salvos na tabela `rpa_protocolos` pelo
`SQLiteStatusRepository`. A pasta `logs/` contém amostras sanitizadas para
documentação e avaliação; o banco local de execução permanece ignorado pelo
Git.

## 6. Critérios de aceite

- Uma ocorrência válida deve gerar protocolo e status `SUCESSO`.
- Timeout deve gerar `ERRO_TIMEOUT` sem protocolo.
- Falha inesperada deve gerar `ERRO` sem interromper o registro.
- O histórico deve exibir as execuções mais recentes primeiro.
