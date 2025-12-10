"""
Cliente para download e processamento de datasets do HuggingFace.

Fornece funções cacheadas para carregar datasets do HuggingFace Hub
e convertê-los para pandas DataFrames com processamento básico.
"""

import logging
from typing import Optional

import pandas as pd
import streamlit as st
from datasets import load_dataset

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600 * 6)  # Cache por 6 horas
def load_hf_dataset(
    dataset_name: str,
    split: str = "train",
    subset: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carrega dataset do HuggingFace e retorna como DataFrame.

    Esta função usa cache do Streamlit para evitar downloads repetidos.
    O cache expira após 6 horas.

    Args:
        dataset_name: Nome do dataset no HuggingFace Hub (ex: "nitaibezerra/govbrnews")
        split: Split a carregar (train/test/validation). Default: "train"
        subset: Subset/configuração do dataset (opcional)

    Returns:
        DataFrame com os dados do dataset

    Raises:
        ValueError: Se dataset não existir ou split for inválido
        Exception: Se ocorrer erro no download ou processamento

    Exemplo:
        >>> df = load_hf_dataset("nitaibezerra/govbrnews-reduced")
        >>> print(df.shape)
        (1000, 10)
    """
    try:
        logger.info(f"Carregando dataset '{dataset_name}' (split: {split})...")

        # Carrega dataset do HuggingFace
        if subset:
            dataset = load_dataset(dataset_name, subset, split=split)
        else:
            dataset = load_dataset(dataset_name, split=split)

        logger.info(f"Dataset carregado. Total de registros: {len(dataset)}")

        # Converte para pandas DataFrame
        df = dataset.to_pandas()

        # Processamento automático de colunas de data
        df = _process_datetime_columns(df)

        logger.info(f"Dataset processado: {len(df)} registros, {len(df.columns)} colunas")
        return df

    except ValueError as e:
        logger.error(f"Erro de validação ao carregar dataset: {e}")
        raise ValueError(
            f"Dataset '{dataset_name}' não encontrado ou split '{split}' inválido. "
            f"Verifique o nome e tente novamente."
        ) from e

    except Exception as e:
        logger.error(f"Erro ao carregar dataset: {e}")
        raise Exception(
            f"Erro ao carregar dataset '{dataset_name}': {str(e)}"
        ) from e


def _process_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa automaticamente colunas que parecem conter datas.

    Detecta colunas com nomes comuns de data/timestamp e converte para datetime.

    Args:
        df: DataFrame a processar

    Returns:
        DataFrame com colunas de data convertidas
    """
    # Padrões comuns de nomes de colunas de data
    date_patterns = [
        "date",
        "time",
        "timestamp",
        "_at",  # created_at, updated_at, published_at, etc
        "_date",
        "_time",
    ]

    for col in df.columns:
        col_lower = col.lower()

        # Verifica se coluna parece conter datas
        if any(pattern in col_lower for pattern in date_patterns):
            try:
                # Tenta converter para datetime
                df[col] = pd.to_datetime(df[col], errors="coerce")
                logger.debug(f"Coluna '{col}' convertida para datetime")
            except Exception as e:
                logger.debug(f"Não foi possível converter '{col}' para datetime: {e}")
                continue

    return df


@st.cache_data
def get_column_stats(df: pd.DataFrame, column: str) -> dict:
    """
    Calcula estatísticas para uma coluna específica.

    Args:
        df: DataFrame contendo a coluna
        column: Nome da coluna para análise

    Returns:
        Dicionário com estatísticas da coluna

    Exemplo:
        >>> stats = get_column_stats(df, "age")
        >>> print(stats["mean"])
        35.5
    """
    stats = {
        "column": column,
        "dtype": str(df[column].dtype),
        "count": len(df[column]),
        "unique": df[column].nunique(),
        "null_count": df[column].isna().sum(),
        "null_pct": (df[column].isna().sum() / len(df[column])) * 100,
    }

    # Estatísticas específicas por tipo
    if pd.api.types.is_numeric_dtype(df[column]):
        stats.update(
            {
                "mean": df[column].mean(),
                "std": df[column].std(),
                "min": df[column].min(),
                "max": df[column].max(),
                "median": df[column].median(),
                "q25": df[column].quantile(0.25),
                "q75": df[column].quantile(0.75),
            }
        )

    return stats
