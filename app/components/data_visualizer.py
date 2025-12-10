"""
Componente para criar visualizações interativas de dados.

Fornece diferentes tipos de gráficos para explorar relações
e distribuições nos dados usando Altair.
"""

import pandas as pd
import streamlit as st
import altair as alt


def create_visualizations(df: pd.DataFrame) -> None:
    """
    Renderiza UI para criar visualizações customizadas.

    Permite escolher tipo de visualização e colunas,
    gerando gráficos interativos conforme a seleção.

    Args:
        df: DataFrame a visualizar

    Exemplo:
        >>> create_visualizations(df)
        # Renderiza UI de seleção e visualizações
    """
    st.subheader("Visualizações Customizadas")

    if df.empty:
        st.warning("DataFrame vazio. Carregue um dataset para começar.")
        return

    # Identificar tipos de colunas
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    if not numeric_cols and not categorical_cols and not datetime_cols:
        st.info("Nenhuma coluna adequada encontrada para visualização")
        return

    # Selectbox para tipo de visualização
    viz_type = st.selectbox(
        "Tipo de Visualização",
        options=[
            "Histograma",
            "Gráfico de Barras",
            "Scatter Plot",
            "Linha Temporal",
            "Box Plot",
            "Mapa de Calor (Correlação)"
        ],
        help="Escolha o tipo de gráfico que deseja criar"
    )

    # Renderiza visualização conforme tipo selecionado
    if viz_type == "Histograma":
        _render_histogram(df, numeric_cols)
    elif viz_type == "Gráfico de Barras":
        _render_bar_chart(df, categorical_cols)
    elif viz_type == "Scatter Plot":
        _render_scatter(df, numeric_cols)
    elif viz_type == "Linha Temporal":
        _render_timeline(df, datetime_cols, numeric_cols, categorical_cols)
    elif viz_type == "Box Plot":
        _render_boxplot(df, numeric_cols, categorical_cols)
    elif viz_type == "Mapa de Calor (Correlação)":
        _render_correlation_heatmap(df, numeric_cols)


def _render_histogram(df: pd.DataFrame, numeric_cols: list) -> None:
    """Renderiza histograma para coluna numérica."""
    if not numeric_cols:
        st.warning("Nenhuma coluna numérica disponível")
        return

    col1, col2 = st.columns(2)

    with col1:
        column = st.selectbox("Coluna", numeric_cols, key="hist_col")

    with col2:
        bins = st.slider("Número de Bins", 10, 100, 30, key="hist_bins")

    # Remove NaN
    clean_df = df[[column]].dropna()

    if len(clean_df) == 0:
        st.warning("Todos os valores são nulos")
        return

    chart = alt.Chart(clean_df).mark_bar(color="#1351B4").encode(
        alt.X(column, bin=alt.Bin(maxbins=bins), title=column),
        alt.Y("count()", title="Frequência"),
        tooltip=[alt.Tooltip(f"{column}:Q", bin=True), "count()"]
    ).properties(
        width=700,
        height=400,
        title=f"Distribuição: {column}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _render_bar_chart(df: pd.DataFrame, categorical_cols: list) -> None:
    """Renderiza gráfico de barras para coluna categórica."""
    if not categorical_cols:
        st.warning("Nenhuma coluna categórica disponível")
        return

    col1, col2 = st.columns(2)

    with col1:
        column = st.selectbox("Coluna", categorical_cols, key="bar_col")

    with col2:
        top_n = st.slider("Top N Valores", 5, 50, 10, key="bar_topn")

    # Remove NaN e pega top N
    value_counts = df[column].value_counts().head(top_n).reset_index()
    value_counts.columns = [column, "count"]

    chart = alt.Chart(value_counts).mark_bar(color="#1351B4").encode(
        x=alt.X("count:Q", title="Frequência"),
        y=alt.Y(f"{column}:N", sort="-x", title=column),
        tooltip=[column, "count"]
    ).properties(
        width=700,
        height=max(300, top_n * 25),  # Altura dinâmica
        title=f"Top {top_n} Valores: {column}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _render_scatter(df: pd.DataFrame, numeric_cols: list) -> None:
    """Renderiza scatter plot para duas colunas numéricas."""
    if len(numeric_cols) < 2:
        st.warning("Necessário pelo menos 2 colunas numéricas")
        return

    col1, col2 = st.columns(2)

    with col1:
        x_col = st.selectbox("Eixo X", numeric_cols, key="scatter_x")

    with col2:
        y_col = st.selectbox(
            "Eixo Y",
            [c for c in numeric_cols if c != x_col],
            key="scatter_y"
        )

    # Remove linhas com NaN
    clean_df = df[[x_col, y_col]].dropna()

    if len(clean_df) == 0:
        st.warning("Nenhum dado válido após remover NaN")
        return

    # Limita a 5000 pontos para performance
    if len(clean_df) > 5000:
        st.info(f"Amostrando 5000 de {len(clean_df)} pontos para melhor performance")
        clean_df = clean_df.sample(5000, random_state=42)

    chart = alt.Chart(clean_df).mark_circle(
        size=60,
        color="#1351B4",
        opacity=0.5
    ).encode(
        x=alt.X(x_col, title=x_col),
        y=alt.Y(y_col, title=y_col),
        tooltip=[x_col, y_col]
    ).properties(
        width=700,
        height=500,
        title=f"Relação: {x_col} vs {y_col}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _render_timeline(
    df: pd.DataFrame,
    datetime_cols: list,
    numeric_cols: list,
    categorical_cols: list
) -> None:
    """Renderiza linha temporal."""
    if not datetime_cols:
        st.warning("Nenhuma coluna de data/hora disponível")
        return

    col1, col2 = st.columns(2)

    with col1:
        date_col = st.selectbox("Coluna de Data", datetime_cols, key="time_date")

    with col2:
        # Escolher entre contar ocorrências ou somar valores
        mode = st.radio(
            "Modo",
            ["Contar Ocorrências", "Somar Valores"],
            key="time_mode"
        )

    value_col = None
    if mode == "Somar Valores" and numeric_cols:
        value_col = st.selectbox("Coluna de Valores", numeric_cols, key="time_value")

    # Preparar dados
    clean_df = df[[date_col] + ([value_col] if value_col else [])].dropna()

    if len(clean_df) == 0:
        st.warning("Nenhum dado válido")
        return

    # Agregar por data
    clean_df["date"] = clean_df[date_col].dt.date

    if mode == "Contar Ocorrências":
        timeline_data = clean_df.groupby("date").size().reset_index(name="value")
        y_title = "Contagem"
    else:
        timeline_data = clean_df.groupby("date")[value_col].sum().reset_index()
        timeline_data.columns = ["date", "value"]
        y_title = f"Soma de {value_col}"

    chart = alt.Chart(timeline_data).mark_line(
        color="#1351B4",
        point=True
    ).encode(
        x=alt.X("date:T", title="Data"),
        y=alt.Y("value:Q", title=y_title),
        tooltip=["date:T", "value:Q"]
    ).properties(
        width=700,
        height=400,
        title=f"Temporal: {date_col}"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def _render_boxplot(
    df: pd.DataFrame,
    numeric_cols: list,
    categorical_cols: list
) -> None:
    """Renderiza box plot."""
    if not numeric_cols:
        st.warning("Nenhuma coluna numérica disponível")
        return

    col1, col2 = st.columns(2)

    with col1:
        value_col = st.selectbox("Coluna de Valores", numeric_cols, key="box_value")

    with col2:
        if categorical_cols:
            group_col = st.selectbox(
                "Agrupar Por (Opcional)",
                ["Nenhum"] + categorical_cols,
                key="box_group"
            )
        else:
            group_col = "Nenhum"

    # Preparar dados
    if group_col == "Nenhum":
        clean_df = df[[value_col]].dropna()

        chart = alt.Chart(clean_df).mark_boxplot(color="#1351B4").encode(
            y=alt.Y(value_col, title=value_col)
        ).properties(
            width=300,
            height=400,
            title=f"Distribuição: {value_col}"
        )
    else:
        clean_df = df[[value_col, group_col]].dropna()

        # Limita categorias para evitar gráfico muito grande
        top_categories = clean_df[group_col].value_counts().head(15).index
        clean_df = clean_df[clean_df[group_col].isin(top_categories)]

        chart = alt.Chart(clean_df).mark_boxplot(color="#1351B4").encode(
            x=alt.X(group_col, title=group_col),
            y=alt.Y(value_col, title=value_col),
            tooltip=[group_col, value_col]
        ).properties(
            width=700,
            height=400,
            title=f"Distribuição de {value_col} por {group_col}"
        )

    st.altair_chart(chart, use_container_width=True)


def _render_correlation_heatmap(df: pd.DataFrame, numeric_cols: list) -> None:
    """Renderiza mapa de calor de correlação."""
    if len(numeric_cols) < 2:
        st.warning("Necessário pelo menos 2 colunas numéricas")
        return

    # Limita a 20 colunas para legibilidade
    if len(numeric_cols) > 20:
        st.info("Mostrando apenas as primeiras 20 colunas numéricas")
        selected_cols = numeric_cols[:20]
    else:
        selected_cols = numeric_cols

    # Calcula correlação
    corr_matrix = df[selected_cols].corr().reset_index().melt("index")
    corr_matrix.columns = ["var1", "var2", "correlation"]

    # Criar heatmap
    chart = alt.Chart(corr_matrix).mark_rect().encode(
        x=alt.X("var1:N", title=""),
        y=alt.Y("var2:N", title=""),
        color=alt.Color(
            "correlation:Q",
            scale=alt.Scale(scheme="blueorange", domain=[-1, 1]),
            title="Correlação"
        ),
        tooltip=["var1", "var2", alt.Tooltip("correlation:Q", format=".2f")]
    ).properties(
        width=600,
        height=600,
        title="Matriz de Correlação"
    )

    st.altair_chart(chart, use_container_width=True)
