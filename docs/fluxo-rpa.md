# Fluxograma do RPA

O fluxo começa com uma ocorrência crítica já validada pelo MVP e termina com o
registro do resultado no SQLite e no histórico da interface.

```mermaid
flowchart TD
    A[Ocorrência crítica validada] --> B[OccurrenceQueue]
    B --> C[RobotZeladoria]
    C --> D{FormClient}
    D -->|Dados válidos| E[Portal SP156 simulado]
    E --> F[Gerar protocolo]
    F --> G[Status SUCESSO]
    D -->|Timeout| H[Status ERRO_TIMEOUT]
    D -->|Outro erro| I[Status ERRO]
    G --> J[StatusRepository]
    H --> J
    I --> J
    J --> K[(SQLite rpa_protocolos)]
    K --> L[Histórico no site]
```

## Pontos principais

1. A fila fornece somente ocorrências validadas.
2. O `RobotZeladoria` coordena o processamento.
3. O cliente do formulário valida os campos e simula o portal.
4. Todo resultado, inclusive falhas, é persistido.
5. A interface consulta o histórico pela rota `/api/history`.
