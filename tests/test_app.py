"""
Testes básicos para o HuggingFace Dataset Explorer.
"""

import pytest
import pandas as pd
from app.utils.huggingface_client import _process_datetime_columns, get_column_stats


def test_process_datetime_columns():
    """Testa processamento automático de colunas de data."""
    df = pd.DataFrame({
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "value": [1, 2, 3],
        "timestamp": ["2024-01-01 10:00:00", "2024-01-02 11:00:00", "2024-01-03 12:00:00"]
    })

    result = _process_datetime_columns(df)

    # Verifica se colunas foram convertidas
    assert pd.api.types.is_datetime64_any_dtype(result["created_at"])
    assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
    assert not pd.api.types.is_datetime64_any_dtype(result["value"])


def test_get_column_stats_numeric():
    """Testa cálculo de estatísticas para coluna numérica."""
    df = pd.DataFrame({"values": [1, 2, 3, 4, 5, None]})

    stats = get_column_stats(df, "values")

    assert stats["column"] == "values"
    assert stats["count"] == 6
    assert stats["unique"] == 5
    assert stats["null_count"] == 1
    assert "mean" in stats
    assert stats["mean"] == pytest.approx(3.0)


def test_get_column_stats_categorical():
    """Testa cálculo de estatísticas para coluna categórica."""
    df = pd.DataFrame({"category": ["A", "B", "A", "C", "A", None]})

    stats = get_column_stats(df, "category")

    assert stats["column"] == "category"
    assert stats["count"] == 6
    assert stats["unique"] == 3  # A, B, C (None não conta como único)
    assert stats["null_count"] == 1
    assert "mean" not in stats  # Não deve ter estatísticas numéricas
