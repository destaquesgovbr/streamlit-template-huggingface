"""
Componente para análise detalhada de colunas de datasets.

Fornece UI interativa para explorar estatísticas, distribuições
e valores de colunas individuais.
"""

import pandas as pd
import streamlit as st
import altair as alt


def analyze_columns(df: pd.DataFrame) -> None:
    """
    Renderiza UI para análise detalhada de colunas.

    Permite selecionar uma coluna e exibe estatísticas relevantes,
    visualizações e amostras de dados conforme o tipo da coluna.

    Args:
        df: DataFrame a analisar

    Exemplo:
        >>> analyze_columns(df)
        # Renderiza selectbox e análises na UI do Streamlit
    """
    st.subheader("Análise Detalhada de Colunas")

    if df.empty:
        st.warning("DataFrame vazio. Carregue um dataset para começar.")
        return

    # Selectbox para escolher coluna
    column = st.selectbox(
        "Selecione uma coluna para análise",
        options=df.columns.tolist(),
        help="Escolha a coluna que deseja explorar em detalhes"
    )

    if not column:
        return

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        _show_basic_info(df, column)

    with col2:
        _show_type_specific_stats(df, column)

    # Visualização (se aplicável)
    _show_column_visualization(df, column)

    # Amostra de valores
    st.write("**Amostra de Valores**")
    sample_size = min(20, len(df))
    st.dataframe(
        df[[column]].head(sample_size),
        use_container_width=True,
        height=300
    )


def _show_basic_info(df: pd.DataFrame, column: str) -> None:
    """Mostra informações básicas da coluna."""
    st.write("**Informações Básicas**")

    dtype = df[column].dtype
    total_count = len(df[column])
    unique_count = df[column].nunique()
    null_count = df[column].isna().sum()
    null_pct = (null_count / total_count) * 100

    st.write(f"- **Tipo:** `{dtype}`")
    st.write(f"- **Total de valores:** {total_count:,}")
    st.write(f"- **Valores únicos:** {unique_count:,}")
    st.write(f"- **Valores nulos:** {null_count:,} ({null_pct:.1f}%)")

    # Indicador de completude
    completeness = 100 - null_pct
    if completeness == 100:
        st.success(f"✓ Completude: {completeness:.1f}%")
    elif completeness >= 90:
        st.info(f"Completude: {completeness:.1f}%")
    else:
        st.warning(f"⚠ Completude: {completeness:.1f}%")


def _show_type_specific_stats(df: pd.DataFrame, column: str) -> None:
    """Mostra estatísticas específicas conforme o tipo da coluna."""
    if pd.api.types.is_numeric_dtype(df[column]):
        _show_numeric_stats(df, column)
    elif pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
        _show_categorical_stats(df, column)
    elif pd.api.types.is_datetime64_any_dtype(df[column]):
        _show_datetime_stats(df, column)
    else:
        st.write("**Estatísticas**")
        st.info("Tipo de dado não suportado para estatísticas detalhadas")


def _show_numeric_stats(df: pd.DataFrame, column: str) -> None:
    """Mostra estatísticas para colunas numéricas."""
    st.write("**Estatísticas (Numérico)**")

    # Remove NaN para cálculos
    clean_data = df[column].dropna()

    if len(clean_data) == 0:
        st.warning("Todos os valores são nulos")
        return

    stats = {
        "Média": f"{clean_data.mean():.2f}",
        "Desvio Padrão": f"{clean_data.std():.2f}",
        "Mínimo": f"{clean_data.min():.2f}",
        "Q25 (25%)": f"{clean_data.quantile(0.25):.2f}",
        "Mediana (50%)": f"{clean_data.quantile(0.50):.2f}",
        "Q75 (75%)": f"{clean_data.quantile(0.75):.2f}",
        "Máximo": f"{clean_data.max():.2f}",
    }

    for label, value in stats.items():
        st.write(f"- **{label}:** {value}")


def _show_categorical_stats(df: pd.DataFrame, column: str) -> None:
    """Mostra estatísticas para colunas categóricas/texto."""
    st.write("**Top 10 Valores Mais Frequentes**")

    value_counts = df[column].value_counts().head(10)

    if len(value_counts) == 0:
        st.warning("Nenhum valor encontrado")
        return

    # Mostra como tabela
    freq_df = pd.DataFrame({
        "Valor": value_counts.index,
        "Frequência": value_counts.values,
        "Percentual": (value_counts.values / len(df) * 100).round(1)
    })

    st.dataframe(freq_df, use_container_width=True, height=300)


def _show_datetime_stats(df: pd.DataFrame, column: str) -> None:
    """Mostra estatísticas para colunas de data/hora."""
    st.write("**Estatísticas (Data/Hora)**")

    # Remove NaN para cálculos
    clean_data = df[column].dropna()

    if len(clean_data) == 0:
        st.warning("Todos os valores são nulos")
        return

    stats = {
        "Data Mais Antiga": clean_data.min().strftime("%Y-%m-%d %H:%M:%S"),
        "Data Mais Recente": clean_data.max().strftime("%Y-%m-%d %H:%M:%S"),
        "Intervalo (dias)": (clean_data.max() - clean_data.min()).days,
    }

    for label, value in stats.items():
        st.write(f"- **{label}:** {value}")


def _show_column_visualization(df: pd.DataFrame, column: str) -> None:
    """Mostra visualização apropriada para a coluna."""
    st.write("**Visualização**")

    # Remove NaN para visualização
    clean_df = df[[column]].dropna()

    if len(clean_df) == 0:
        st.warning("Todos os valores são nulos - visualização não disponível")
        return

    if pd.api.types.is_numeric_dtype(df[column]):
        _plot_histogram(clean_df, column)
    elif pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
        _plot_bar_chart(clean_df, column)
    elif pd.api.types.is_datetime64_any_dtype(df[column]):
        _plot_timeline(clean_df, column)
    else:
        st.info("Visualização não disponível para este tipo de dado")


def _plot_histogram(df: pd.DataFrame, column: str) -> None:
    """Plota histograma para coluna numérica."""
    chart = alt.Chart(df).mark_bar(color="#1351B4").encode(
        alt.X(column, bin=alt.Bin(maxbins=30), title=column),
        alt.Y("count()", title="Frequência"),
        tooltip=[alt.Tooltip(f"{column}:Q", bin=True, title=column), "count()"]
    ).properties(
        width=600,
        height=300,
        title=f"Distribuição: {column}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _plot_bar_chart(df: pd.DataFrame, column: str) -> None:
    """Plota gráfico de barras para coluna categórica."""
    # Top 15 valores
    value_counts = df[column].value_counts().head(15).reset_index()
    value_counts.columns = [column, "count"]

    chart = alt.Chart(value_counts).mark_bar(color="#1351B4").encode(
        x=alt.X("count:Q", title="Frequência"),
        y=alt.Y(f"{column}:N", sort="-x", title=column),
        tooltip=[column, "count"]
    ).properties(
        width=600,
        height=400,
        title=f"Top 15 Valores: {column}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _plot_timeline(df: pd.DataFrame, column: str) -> None:
    """Plota linha temporal para coluna de data."""
    # Agrupa por data e conta
    df_timeline = df.copy()
    df_timeline["date"] = df_timeline[column].dt.date
    counts = df_timeline.groupby("date").size().reset_index(name="count")

    chart = alt.Chart(counts).mark_line(color="#1351B4", point=True).encode(
        x=alt.X("date:T", title="Data"),
        y=alt.Y("count:Q", title="Frequência"),
        tooltip=["date:T", "count:Q"]
    ).properties(
        width=600,
        height=300,
        title=f"Distribuição Temporal: {column}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
