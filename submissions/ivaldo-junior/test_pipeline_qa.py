import pytest
import pandas as pd
import numpy as np
import os
from lead_scorer import load_and_merge_data, calculate_historical_baselines, score_active_pipeline

BASE_PATH = "./"

def test_data_integrity():
    """
    1. test_data_integrity(): Verifica se os 4 ficheiros CSV existem, contêm dados e se o merge é realizado sem perda indevida de linhas.
    """
    assert os.path.exists(f"{BASE_PATH}accounts.csv")
    assert os.path.exists(f"{BASE_PATH}products.csv")
    assert os.path.exists(f"{BASE_PATH}sales_teams.csv")
    assert os.path.exists(f"{BASE_PATH}sales_pipeline.csv")
    
    df = load_and_merge_data(base_path=BASE_PATH)
    assert not df.empty, "O DataFrame gerado não deve estar vazio."
    
    # Verifica se colunas fundamentais do merge existem
    expected_cols = ['account', 'product', 'sales_agent', 'deal_stage']
    for col in expected_cols:
        assert col in df.columns, f"A coluna '{col}' deve existir após o merge."

def test_schema_resilience():
    """
    2. test_schema_resilience(): Simula variações nos nomes das colunas (ex.: coluna nomeada como 'stage' em vez de 'deal_stage')
    e valida se o carregador trata o schema sem lançar exceções.
    """
    # Create mock CSVs with different schema ('stage' instead of 'deal_stage')
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Mock accounts
        pd.DataFrame({'account': ['A']}).to_csv(f"{tmpdirname}/accounts.csv", index=False)
        # Mock products
        pd.DataFrame({'product': ['P']}).to_csv(f"{tmpdirname}/products.csv", index=False)
        # Mock teams
        pd.DataFrame({'sales_agent': ['S']}).to_csv(f"{tmpdirname}/sales_teams.csv", index=False)
        # Mock pipeline with 'stage' instead of 'deal_stage'
        pd.DataFrame({'account': ['A'], 'product': ['P'], 'sales_agent': ['S'], 'stage': ['Engaging'], 'created_on': ['2023-01-01']}).to_csv(f"{tmpdirname}/sales_pipeline.csv", index=False)
        
        # Load and test
        try:
            df = load_and_merge_data(base_path=f"{tmpdirname}/")
            assert not df.empty
            assert 'deal_stage' in df.columns, "O script deve converter 'stage' para 'deal_stage'."
        except Exception as e:
            pytest.fail(f"O pipeline falhou ao tratar schema com resiliência: {e}")

def test_scoring_boundaries():
    """
    3. test_scoring_boundaries(): Garante que todos os scores gerados estejam estritamente contidos no intervalo de 0 a 100
    e que nenhuma probabilidade calculada seja negativa.
    """
    df = load_and_merge_data(base_path=BASE_PATH)
    baselines = calculate_historical_baselines(df)
    df_scored = score_active_pipeline(df, baselines)
    
    if not df_scored.empty:
        assert (df_scored['Lead Score'] >= 0).all(), "Existem scores menores que 0."
        assert (df_scored['Lead Score'] <= 100).all(), "Existem scores maiores que 100."

def test_explainability_not_empty():
    """
    4. test_explainability_not_empty(): Assegura que todas as oportunidades ativas possuam uma justificativa textual preenchida e coerente.
    """
    df = load_and_merge_data(base_path=BASE_PATH)
    baselines = calculate_historical_baselines(df)
    df_scored = score_active_pipeline(df, baselines)
    
    if not df_scored.empty:
        # Verifica NaN
        assert not df_scored['Explainability'].isna().any(), "Existem campos de explicabilidade nulos."
        # Verifica se o comprimento da string é maior que 0
        assert (df_scored['Explainability'].str.len() > 0).all(), "Existem justificativas vazias."

def test_empty_filter_safety():
    """
    5. test_empty_filter_safety(): Testa o comportamento da filtragem quando nenhum lead atende aos critérios,
    validando a estabilidade da aplicação sem crash.
    (Aqui simulamos o filtro retornando vazio no DataFrame)
    """
    df = load_and_merge_data(base_path=BASE_PATH)
    baselines = calculate_historical_baselines(df)
    df_scored = score_active_pipeline(df, baselines)
    
    # Simula um filtro que não retorna nada
    df_empty = df_scored[df_scored['manager'] == 'Filtro Inexistente']
    
    # As métricas e o código devem suportar um df_empty sem lançar exceções.
    try:
        total_leads_filtrados = len(df_empty)
        alta_prioridade = len(df_empty[df_empty['Priority'] == "🔥 Alta Prioridade"])
        valor_pipeline = df_empty['close_value'].sum()
        conversao_esperada = df_empty['Lead Score'].mean()
        
        # Validando resultados seguros (pandas fillna behaviour)
        assert total_leads_filtrados == 0
        assert alta_prioridade == 0
        assert valor_pipeline == 0
        # A média de array vazio no pandas é NaN. Tratamento no front deve lidar com isso.
        assert pd.isna(conversao_esperada) or conversao_esperada >= 0
    except Exception as e:
        pytest.fail(f"Operações matemáticas sobre dataframe filtrado vazio lançaram erro: {e}")
