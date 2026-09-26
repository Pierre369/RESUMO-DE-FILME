"""
Módulo de Estruturação e Validação de Roteiro Cinematográfico em 1ª Pessoa.
"""

from typing import Dict, Any, List

class ScreenplayManager:
    """
    Gerencia as regras de escrita e formatação dramática em primeira pessoa
    para vídeos verticais de curta duração (~3 minutos).
    """

    TARGET_WPM = 150  # Palavras por minuto em cadência cinematográfica pausada
    TARGET_DURATION_MIN = 3.0
    IDEAL_WORD_COUNT = 450  # ~450 a 500 palavras

    DRAMATIC_STRUCTURE = {
        "Ato 1": {
            "name": "Apresentação e Dilema Inicial",
            "time_range": "0:00 - 0:45",
            "focus": "O que o personagem queria no início, a rotina quebrada e o catalisador do conflito."
        },
        "Ato 2": {
            "name": "Confronto e Ponto de Não Retorno",
            "time_range": "0:45 - 2:00",
            "focus": "As decisões difíceis, os sacrifícios enfrentados, como as ações afetaram os entes queridos."
        },
        "Ato 3": {
            "name": "Resolução, Preço e Nova Identidade",
            "time_range": "2:00 - 3:00",
            "focus": "O preço pago, a solidão ou triunfo, e como o protagonista enxerga o futuro após os acontecimentos."
        }
    }

    @staticmethod
    def validate_script(text: str) -> Dict[str, Any]:
        """
        Analisa o texto do roteiro e estima a duração e conformidade com as regras dramáticas.
        """
        words = text.strip().split()
        word_count = len(words)
        estimated_duration_sec = (word_count / ScreenplayManager.TARGET_WPM) * 60.0

        return {
            "word_count": word_count,
            "estimated_duration_sec": round(estimated_duration_sec, 2),
            "target_duration_sec": ScreenplayManager.TARGET_DURATION_MIN * 60,
            "status": "IDEAL" if 400 <= word_count <= 520 else ("CURTO" if word_count < 400 else "LONGO"),
            "advice": (
                "Contagem perfeita para 3 minutos com cadência dramática."
                if 400 <= word_count <= 520 else
                f"Ajuste o número de palavras para ficar em torno de {ScreenplayManager.IDEAL_WORD_COUNT} palavras."
            )
        }
