import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Carregar os dados
file_path = os.path.join("data", "raw", "Base_Trabalho II.xlsx")
df = pd.read_excel(file_path)

# 1. Preparação das Variáveis 
# Criar dummies para a região (deixando uma categoria de base out para não cair em multicolinearidade)
df = pd.get_dummies(df, columns=['regiao'], drop_first=True, dtype=int)
covariates = [
    'gasto_90d', 'frequencia_90d', 'recencia_dias', 
    'visitas_app_30d', 'taxa_abertura_email', 
    'tempo_cliente_meses', 'assinante_premium'
] + [col for col in df.columns if col.startswith('regiao_')]

# 2. Estimar o Propensity Score (PS) via Regressão Logística
X = df[covariates]
X = sm.add_constant(X)
y = df['recebeu_cupom']

# Modelo logit para prever a probabilidade de receber o cupom
logit_model = sm.Logit(y, X)
result = logit_model.fit(disp=False)
df['propensity_score'] = result.predict(X)

# Trimming: limitar probabilidades muito extremas para não gerar pesos infinitos (1% - 99%)
df['propensity_score'] = np.clip(df['propensity_score'], 0.01, 0.99)

# 3. Analisar Suporte Comum (Gráfico)
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='propensity_score', hue='recebeu_cupom', kde=True, bins=30, stat="density", common_norm=False)
plt.title('Distribuição do Propensity Score (Suporte Comum)')
plt.xlabel('Propensity Score (Probabilidade Estimada de Receber Cupom)')
plt.ylabel('Densidade')
plt.savefig(os.path.join("output", "figures", "common_support.png"))
plt.close()

# 4. Calcular pesos IPW (ATE - Average Treatment Effect)
# O peso cria uma "população sintética" onde as distribuições das covariáveis são iguais entre tratados e controle.
df['ipw_ate'] = np.where(
    df['recebeu_cupom'] == 1,
    1 / df['propensity_score'],
    1 / (1 - df['propensity_score'])
)

# 5. Estimação do Efeito Causal usando Regressão Ponderada (WLS) Duplamente Robusta
# Usar a regressão ponderada com as covariáveis nos dá a propriedade de "Double Robustness".
formula = 'gasto_30d ~ recebeu_cupom + gasto_90d + frequencia_90d + recencia_dias + visitas_app_30d + taxa_abertura_email + tempo_cliente_meses + assinante_premium + ' + ' + '.join([col for col in df.columns if col.startswith('regiao_')])

# Cov_type='HC3' para lidar com heterocedasticidade gerada pelos pesos
model_ate = smf.wls(formula=formula, data=df, weights=df['ipw_ate']).fit(cov_type='HC3')

print("\n=== EFEITO CAUSAL (IPW + Regressão Duplamente Robusta ATE) ===")
print(f"Estimativa do Efeito Causal (Cupom): R$ {model_ate.params['recebeu_cupom']:.2f}")
print(f"Erro Padrão Robusto: R$ {model_ate.bse['recebeu_cupom']:.2f}")
print(f"P-valor: {model_ate.pvalues['recebeu_cupom']:.4f}")
print(f"Intervalo de Confiança (95%): [R$ {model_ate.conf_int().loc['recebeu_cupom', 0]:.2f}, R$ {model_ate.conf_int().loc['recebeu_cupom', 1]:.2f}]")

# Efeito Naive para comparação
naive_diff = df[df['recebeu_cupom'] == 1]['gasto_30d'].mean() - df[df['recebeu_cupom'] == 0]['gasto_30d'].mean()
print(f"\n=== COMPARAÇÃO ===")
print(f"Efeito Ingênuo (com viés de seleção): R$ {naive_diff:.2f}")
print(f"Efeito Causal Real: R$ {model_ate.params['recebeu_cupom']:.2f}")
print(f"Viés Estimado que inflava os resultados: R$ {naive_diff - model_ate.params['recebeu_cupom']:.2f}")

# 6. Checagem de balanceamento após o peso IPW
bal_results = []
for cov in covariates:
    # Média bruta
    mean_t_raw = df.loc[df['recebeu_cupom'] == 1, cov].mean()
    mean_c_raw = df.loc[df['recebeu_cupom'] == 0, cov].mean()
    diff_raw = mean_t_raw - mean_c_raw
    
    # Média ponderada tratados
    mean_t_w = np.average(df.loc[df['recebeu_cupom'] == 1, cov], weights=df.loc[df['recebeu_cupom'] == 1, 'ipw_ate'])
    # Média ponderada controle
    mean_c_w = np.average(df.loc[df['recebeu_cupom'] == 0, cov], weights=df.loc[df['recebeu_cupom'] == 0, 'ipw_ate'])
    diff_w = mean_t_w - mean_c_w
    
    bal_results.append({
        'Variável': cov,
        'Diferença Original': round(diff_raw, 2),
        'Diferença Após Peso IPW': round(diff_w, 2),
        'Média Tratados IPW': round(mean_t_w, 2),
        'Média Controle IPW': round(mean_c_w, 2)
    })

print("\n=== BALANCEAMENTO DAS COVARIÁVEIS APÓS IPW ===")
df_bal = pd.DataFrame(bal_results)
print(df_bal.to_markdown(index=False))

# Salvar tabelas
df_bal.to_csv(os.path.join("output", "tables", "balanceamento_ipw.csv"), index=False)
with open(os.path.join("output", "tables", "resultados_causais.txt"), "w") as f:
    f.write(model_ate.summary().as_text())
