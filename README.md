# HuggingFace Dataset Explorer 🤗

Template para criar aplicações Streamlit que exploram e analisam datasets do HuggingFace Hub.

## Sobre

Este template fornece uma estrutura completa e componentes reutilizáveis para construir apps de exploração de dados a partir de datasets do HuggingFace. Inclui funcionalidades de:

- 📊 Carregamento automático de datasets com cache inteligente
- 🔍 Análise detalhada de colunas (estatísticas, distribuições, valores nulos)
- 📈 Visualizações interativas (histogramas, scatter plots, mapas de correlação)
- 💾 Cache de 6 horas para evitar downloads repetidos
- 🎨 Interface em Português BR com tema DGB

## Quando Usar

Este template é ideal quando você precisa:

- Explorar datasets do HuggingFace de forma rápida e interativa
- Criar dashboards de análise exploratória de dados
- Compartilhar datasets com equipes não-técnicas
- Prototipar análises antes de implementação completa
- Demonstrar características de um dataset publicamente

## Como Usar

### Desenvolvimento Local

1. **Clone ou baixe este template:**
```bash
git clone https://github.com/destaquesgovbr/streamlit-template-huggingface.git
cd streamlit-template-huggingface
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute o app:**
```bash
streamlit run app/main.py
```

4. **Acesse no navegador:** http://localhost:8501

### Adaptando para Seu Dataset

Para usar com seu próprio dataset:

1. **Edite `app/main.py`** - Linha 45:
```python
suggested_datasets = [
    "",
    "seu-usuario/seu-dataset",  # Adicione seu dataset aqui
    "nitaibezerra/govbrnews-reduced",
    "Outro...",
]
```

2. **Personalize cores e tema** em `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1351B4"  # Azul DGB (modifique se quiser)
```

3. **Adapte componentes** conforme necessário:
   - `app/components/column_analyzer.py` - Análise de colunas
   - `app/components/data_visualizer.py` - Visualizações
   - `app/utils/huggingface_client.py` - Cliente HuggingFace

## Estrutura de Arquivos

```
streamlit-template-huggingface/
├── app/
│   ├── main.py                      # Aplicação principal (classe DatasetExplorer)
│   ├── components/
│   │   ├── column_analyzer.py       # Análise detalhada de colunas
│   │   └── data_visualizer.py       # Visualizações interativas
│   └── utils/
│       └── huggingface_client.py    # Cliente para HuggingFace Hub
├── tests/
│   └── test_app.py                  # Testes básicos
├── .github/workflows/
│   └── build-deploy.yml             # CI/CD para Cloud Run
├── .streamlit/
│   └── config.toml                  # Configuração do Streamlit
├── .streamlit-app.yaml              # Metadados para catálogo
├── Dockerfile                       # Container para deploy
├── requirements.txt                 # Dependências Python
├── .dockerignore
├── .gitignore
├── README.md
└── LICENSE
```

## Componentes Reutilizáveis

### 1. HuggingFace Client (`app/utils/huggingface_client.py`)

```python
from utils.huggingface_client import load_hf_dataset

# Carrega dataset com cache de 6 horas
df = load_hf_dataset("nitaibezerra/govbrnews-reduced")
```

**Recursos:**
- Cache automático via `@st.cache_data(ttl=3600*6)`
- Processamento automático de colunas de data
- Tratamento de erros com mensagens claras
- Suporta diferentes splits e subsets

### 2. Column Analyzer (`app/components/column_analyzer.py`)

```python
from components.column_analyzer import analyze_columns

# Renderiza UI de análise
analyze_columns(df)
```

**Recursos:**
- Estatísticas por tipo (numérico, categórico, temporal)
- Visualizações inline (histogramas, barras, timeline)
- Detecção de valores nulos e completude
- Amostra de dados

### 3. Data Visualizer (`app/components/data_visualizer.py`)

```python
from components.data_visualizer import create_visualizations

# Renderiza UI de visualizações
create_visualizations(df)
```

**Recursos:**
- 6 tipos de visualizações (histograma, barras, scatter, timeline, boxplot, heatmap)
- Configuração interativa (bins, top N, colunas)
- Performance otimizada (amostragem para grandes datasets)
- Gráficos responsivos com Altair

## Personalização

### Modificar Cores e Tema

Edite `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1351B4"      # Cor principal (azul DGB)
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Adicionar Novos Tipos de Visualização

Edite `app/components/data_visualizer.py` e adicione nova função:

```python
def _render_minha_viz(df: pd.DataFrame, cols: list) -> None:
    """Nova visualização customizada."""
    # Seu código Altair aqui
    pass
```

### Processar Dados Customizados

Edite `app/utils/huggingface_client.py` para adicionar lógica de processamento:

```python
def _process_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adicione sua lógica de processamento aqui."""
    # Exemplo: extrair features de data
    df["day_of_week"] = df["date_column"].dt.dayofweek
    return df
```

## Deploy

Este template está pronto para deploy na Plataforma Streamlit DGB via Cloud Run.

### Registrar App

1. Vá para o repositório [destaquesgovbr-infra](https://github.com/destaquesgovbr/destaquesgovbr-infra)

2. Abra uma issue usando o template **"Registrar App Streamlit"**

3. Preencha os dados:
   - **Nome do App:** `template-huggingface` (ou seu nome customizado)
   - **Repositório:** `streamlit-template-huggingface` (ou seu repo)
   - **Descrição:** Descrição do seu app
   - **Resource Tier:** `small` (adequado para exploração de datasets)
   - **Min Instances:** `0` (escala para zero quando não usado)

4. Aguarde a criação automática do PR

5. Após merge, o app estará disponível em Cloud Run

### Configurar Secrets (se necessário)

Se seu app precisar de secrets:

```bash
cd /caminho/para/seu-repo
gh secret set NOME_DO_SECRET --body "valor"
```

## Exemplos

### Exemplo 1: Dataset de Notícias GovBR

```python
# Em app/main.py, já está configurado
suggested_datasets = [
    "nitaibezerra/govbrnews-reduced",  # Dataset de exemplo
]
```

Recursos do dataset:
- ~1000 artigos de notícias do portal gov.br
- Colunas: título, conteúdo, agência, data de publicação
- Ideal para análise temporal e por agência

### Exemplo 2: Seu Próprio Dataset

1. Faça upload do seu dataset para HuggingFace Hub
2. Adicione ao `suggested_datasets`
3. App funcionará automaticamente com qualquer dataset pandas-compatível

## Testes

Execute os testes:

```bash
pytest tests/
```

## Contribuindo

Este é um template mantido pelo DGB Team. Para sugestões:

1. Fork este repositório
2. Crie uma branch para sua feature
3. Submeta um Pull Request

## Licença

AGPL-3.0 License - veja [LICENSE](LICENSE) para detalhes

## Suporte

- **Documentação:** [GitHub Wiki](https://github.com/destaquesgovbr/streamlit-template-huggingface/wiki)
- **Issues:** [GitHub Issues](https://github.com/destaquesgovbr/streamlit-template-huggingface/issues)
- **HuggingFace Datasets:** https://huggingface.co/datasets

---

**Desenvolvido com** 💙 **pelo DGB Team**
