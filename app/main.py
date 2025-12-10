"""
HuggingFace Dataset Explorer Template

Template para criar apps que exploram datasets do HuggingFace.
Inclui componentes reutilizáveis para seleção, análise e visualização de dados.

Exemplo de uso:
    streamlit run app/main.py
"""

import streamlit as st
import pandas as pd

from utils.huggingface_client import load_hf_dataset
from components.column_analyzer import analyze_columns
from components.data_visualizer import create_visualizations

# Configuração da página
st.set_page_config(
    page_title="HuggingFace Dataset Explorer",
    page_icon="🤗",
    layout="wide",
)


class DatasetExplorer:
    """
    Classe para encapsular lógica de exploração de datasets.

    Gerencia carregamento, análise e visualização de datasets do HuggingFace.

    Attributes:
        df: DataFrame carregado do HuggingFace
        dataset_name: Nome do dataset atual
    """

    def __init__(self):
        """Inicializa o explorador de datasets."""
        self.df: pd.DataFrame = None
        self.dataset_name: str = ""

    def render_sidebar(self) -> tuple[str, str]:
        """
        Renderiza configurações na sidebar.

        Returns:
            Tupla (dataset_name, split) selecionados

        Exemplo:
            >>> explorer = DatasetExplorer()
            >>> dataset, split = explorer.render_sidebar()
        """
        with st.sidebar:
            st.header("⚙ Configuração")

            # Datasets sugeridos do DGB
            suggested_datasets = [
                "",  # Opção vazia para forçar seleção
                "nitaibezerra/govbrnews-reduced",
                "nitaibezerra/govbrnews",
                "Outro...",
            ]

            dataset_choice = st.selectbox(
                "Dataset Sugerido",
                options=suggested_datasets,
                help="Escolha um dataset ou selecione 'Outro...' para inserir manualmente",
            )

            # Campo customizado se escolher "Outro..."
            if dataset_choice == "Outro...":
                dataset_name = st.text_input(
                    "Nome do Dataset",
                    placeholder="usuario/nome-do-dataset",
                    help="Ex: nitaibezerra/govbrnews",
                )
            else:
                dataset_name = dataset_choice

            # Seletor de split
            split = st.selectbox(
                "Split",
                options=["train", "test", "validation"],
                index=0,
                help="Qual split do dataset carregar",
            )

            # Botão de carregar
            load_button = st.button(
                "🔄 Carregar Dataset",
                use_container_width=True,
                type="primary",
                disabled=not dataset_name or dataset_name == "",
            )

            return dataset_name, split, load_button

    def load_dataset(self, dataset_name: str, split: str) -> None:
        """
        Carrega dataset do HuggingFace.

        Args:
            dataset_name: Nome do dataset
            split: Split a carregar

        Raises:
            Exception: Se ocorrer erro no carregamento
        """
        try:
            with st.spinner(f"Carregando {dataset_name}..."):
                self.df = load_hf_dataset(dataset_name, split)
                self.dataset_name = dataset_name

            st.success(
                f"✅ Dataset carregado: {len(self.df):,} registros, "
                f"{len(self.df.columns)} colunas"
            )

        except ValueError as e:
            st.error(f"❌ Erro de validação: {e}")
            st.info(
                "💡 **Dica:** Verifique se o nome do dataset está correto. "
                "Você pode encontrar datasets em https://huggingface.co/datasets"
            )

        except Exception as e:
            st.error(f"❌ Erro ao carregar dataset: {e}")

    def render_overview_tab(self) -> None:
        """Renderiza tab de visão geral do dataset."""
        st.subheader("Visão Geral do Dataset")

        if self.df is None or self.df.empty:
            st.info("👈 Selecione um dataset na sidebar para começar")
            return

        # Métricas em colunas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Registros", f"{len(self.df):,}")

        with col2:
            st.metric("Colunas", len(self.df.columns))

        with col3:
            memory_mb = self.df.memory_usage(deep=True).sum() / 1024**2
            st.metric("Tamanho", f"{memory_mb:.1f} MB")

        with col4:
            null_pct = (self.df.isna().sum().sum() / self.df.size) * 100
            st.metric("Dados Completos", f"{100-null_pct:.1f}%")

        # Preview dos dados
        st.subheader("Preview dos Dados")

        # Número de linhas para preview
        preview_rows = st.slider(
            "Linhas para preview",
            min_value=5,
            max_value=min(500, len(self.df)),
            value=min(100, len(self.df)),
            step=5,
        )

        st.dataframe(
            self.df.head(preview_rows),
            use_container_width=True,
            height=400,
        )

        # Informações das colunas
        st.subheader("Informações das Colunas")

        col_info = pd.DataFrame(
            {
                "Tipo": self.df.dtypes.astype(str),
                "Valores Únicos": self.df.nunique(),
                "Valores Nulos": self.df.isna().sum(),
                "% Nulos": (self.df.isna().sum() / len(self.df) * 100).round(1),
            }
        )

        st.dataframe(col_info, use_container_width=True)

    def run(self) -> None:
        """
        Executa o aplicativo principal.

        Renderiza UI completa com sidebar, tabs e componentes.
        """
        # Título principal
        st.title("🤗 HuggingFace Dataset Explorer")

        st.markdown(
            """
            Template para explorar e analisar datasets do [HuggingFace Hub](https://huggingface.co/datasets).

            **Recursos:**
            - 📊 Carregamento automático de datasets
            - 🔍 Análise detalhada de colunas
            - 📈 Visualizações interativas
            - 💾 Cache inteligente (6 horas)
            """
        )

        # Sidebar com configurações
        dataset_name, split, load_button = self.render_sidebar()

        # Carregar dataset se botão pressionado
        if load_button and dataset_name:
            self.load_dataset(dataset_name, split)

        # Mostrar nome do dataset atual se carregado
        if self.df is not None:
            st.info(f"📦 **Dataset Atual:** `{self.dataset_name}` (split: `{split}`)")

        # Tabs para diferentes análises
        tab1, tab2, tab3 = st.tabs(
            ["📊 Visão Geral", "🔍 Análise de Colunas", "📈 Visualizações"]
        )

        with tab1:
            self.render_overview_tab()

        with tab2:
            if self.df is not None and not self.df.empty:
                analyze_columns(self.df)
            else:
                st.info("👈 Carregue um dataset para começar a análise")

        with tab3:
            if self.df is not None and not self.df.empty:
                create_visualizations(self.df)
            else:
                st.info("👈 Carregue um dataset para criar visualizações")

        # Footer
        st.divider()
        st.caption(
            "💡 **Dica:** Use este template como base para criar seus próprios apps de análise de dados!"
        )


def main():
    """Ponto de entrada principal do aplicativo."""
    explorer = DatasetExplorer()
    explorer.run()


if __name__ == "__main__":
    main()
