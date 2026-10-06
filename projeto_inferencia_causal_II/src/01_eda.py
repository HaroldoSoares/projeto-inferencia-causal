import pandas as pd
import numpy as np
from scipy import stats
import os

# Caminho do arquivo
file_path = os.path.join("data", "raw", "Base_Trabalho II.xlsx")

# Carregar os dados
df = pd.read_excel(file_path)

# Covariáveis pré-tratamento (contínuas e binárias para a média)
covariates = [
    'gasto_90d', 
    'frequencia_90d', 
    'recencia_dias', 
    'visitas_app_30d', 
    'taxa_abertura_email', 
    'tempo_cliente_meses', 
    'assinante_premium'
]

# Separar os grupos
treated = df[df['recebeu_cupom'] == 1]
control = df[df['recebeu_cupom'] == 0]

# Tabela de estatísticas descritivas
results = []
for cov in covariates:
    mean_t = treated[cov].mean()
    mean_c = control[cov].mean()
    std_t = treated[cov].std()
    std_c = control[cov].std()
    
    # Teste t para diferença de médias
    t_stat, p_val = stats.ttest_ind(treated[cov], control[cov], equal_var=False)
    
    results.append({
        'Variável': cov,
        'Média Tratados (Cupom=1)': round(mean_t, 2),
        'Média Controle (Cupom=0)': round(mean_c, 2),
        'Diferença (T - C)': round(mean_t - mean_c, 2),
        'P-valor (T-test)': round(p_val, 4)
    })

df_results = pd.DataFrame(results)

# Salvar tabela de resultados
output_path = os.path.join("output", "tables", "tabela_descritiva_pre_campanha.csv")
df_results.to_csv(output_path, index=False)

print("=== ANÁLISE DESCRITIVA: DIFERENÇAS PRÉ-TRATAMENTO ===")
print(df_results.to_markdown(index=False))

# Analisar a distribuição regional (variável categórica)
print("\n=== DISTRIBUIÇÃO REGIONAL ===")
regiao_dist = pd.crosstab(df['regiao'], df['recebeu_cupom'], normalize='columns') * 100
regiao_dist.columns = ['Controle (%)', 'Tratados (%)']
print(regiao_dist.round(2).to_markdown())

# Diferença ingênua (Gasto nos 30 dias seguintes)
naive_diff = treated['gasto_30d'].mean() - control['gasto_30d'].mean()
print(f"\n=== DIFERENÇA INGÊNUA (NAIVE) DE GASTO (30 DIAS) ===")
print(f"Média Tratados: R$ {treated['gasto_30d'].mean():.2f}")
print(f"Média Controle: R$ {control['gasto_30d'].mean():.2f}")
print(f"Diferença Ingênua: R$ {naive_diff:.2f}")

