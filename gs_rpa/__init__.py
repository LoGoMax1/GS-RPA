"""Pacote principal da automação GS-RPA."""

# Reexporta os contratos e o robô para facilitar os imports de quem usa o pacote.
from .robot import FormClient, OccurrenceQueue, ProtocolResult, RobotZeladoria, StatusRepository

# Define explicitamente quais nomes fazem parte da API pública do pacote.
__all__ = [
    "FormClient",
    "OccurrenceQueue",
    "ProtocolResult",
    "RobotZeladoria",
    "StatusRepository",
]
