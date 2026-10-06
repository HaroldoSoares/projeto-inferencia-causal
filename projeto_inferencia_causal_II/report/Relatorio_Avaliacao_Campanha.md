# Avaliação Causal da Campanha de Cupom Personalizado

## 1. Pergunta de Pesquisa
**Qual foi o efeito causal do recebimento do cupom de desconto de 20% sobre o gasto dos clientes nos 30 dias seguintes à campanha?**

A empresa precisa saber se a oferta efetivamente induziu o aumento de gastos ou se os clientes selecionados já apresentavam um comportamento natural de gastar mais. O objetivo não é apenas analisar quem gastou mais, mas quantificar a parcela de aumento de receita exclusivamente atribuível à intervenção do cupom.

## 2. Evidências Descritivas e Viés de Seleção
A campanha apresentou um viés de seleção claro: a atribuição do cupom não foi aleatória e concentrou-se em clientes com maior engajamento.

A tabela abaixo evidencia as diferenças de perfil **antes** da campanha:

| Variável Pré-Tratamento | Média Tratados (Cupom = 1) | Média Controle (Cupom = 0) | Diferença (T - C) | P-Valor (Teste t) |
| :--- | :--- | :--- | :--- | :--- |
| **Gasto (90 dias)** | R$ 800,33 | R$ 502,75 | + R$ 297,57 | < 0.001 |
| **Frequência (90 dias)** | 6,18 | 3,89 | + 2,28 compras | < 0.001 |
| **Recência** | 17,09 dias | 28,17 dias | - 11,08 dias | < 0.001 |
| **Visitas App (30 dias)** | 7,60 | 5,47 | + 2,14 visitas | < 0.001 |
| **Assinante Premium** | 44% | 22% | + 22 p.p. | < 0.001 |

A evidência mostra que o sistema de segmentação favoreceu os "melhores" clientes, que compravam mais e acessavam mais o aplicativo. Portanto, uma comparação direta das médias futuras estaria **enviesada positivamente**.

## 3. Definição das Variáveis
- **Variável de Resultado (Target):** `gasto_30d` (gasto total nos 30 dias após a campanha).
- **Tratamento:** `recebeu_cupom` (variável binária 1/0).
- **Características Prévias (Covariáveis):** Gasto prévio (`gasto_90d`), frequência (`frequencia_90d`), recência (`recencia_dias`), engajamento app (`visitas_app_30d`), engajamento e-mail (`taxa_abertura_email`), tempo de cliente (`tempo_cliente_meses`), assinatura (`assinante_premium`) e região.

## 4. Estratégia de Identificação
Dado que a atribuição foi baseada no comportamento observável, adotamos a premissa de **Seleção em Observáveis** (Unconfoundedness). Nossa estratégia metodológica consistiu no **Inverse Probability Weighting (IPW)** combinado com uma **Regressão Linear Duplamente Robusta**.

**Justificativa Metodológica:**
1. **Propensity Score:** Usamos um modelo logístico para prever a probabilidade de cada cliente receber o cupom com base em seu histórico prévio. 
2. **Ponderação (IPW):** Ponderamos a amostra pelo inverso do Propensity Score. Clientes no grupo de controle que eram muito parecidos com o grupo de tratamento receberam um peso maior. Isso criou uma amostra sinteticamente balanceada.
3. **Double Robustness:** Adicionamos os pesos a uma regressão linear múltipla (controlando pelas covariáveis), blindando a estimativa final. Se a regressão *ou* o cálculo dos pesos estiverem corretos, o estimador será consistente.

## 5. Resultados e Diagnósticos

### Balanceamento (Diagnóstico)
Após o IPW, o viés das covariáveis foi mitigado. O gap de gasto prévio que era de R$ 297,57 despencou para apenas -R$ 6,52. O gap de assinantes premium caiu de 22% para 0%. Existe **suporte comum** e clientes comparáveis em ambas as amostras.

### Estimação Causal vs. Efeito Ingênuo

* **Efeito Ingênuo (Com Viés):** R$ 144,56
* **EFEITO CAUSAL ESTIMADO:** **R$ 48,86**
* **Viés Removido:** R$ 95,70
* **Erro Padrão Robusto:** R$ 1,02
* **Intervalo de Confiança (95%):** [R$ 46,86, R$ 50,86]
* **Significância:** p-valor < 0.001

## 6. Hipóteses Assumidas
Para que a estimativa seja válida sob a ótica causal, assumimos:
1. **Unconfoundedness (Independência Condicional):** Assumimos que *todas* as variáveis importantes que o modelo de marketing usou para distribuir o cupom estão presentes no dataset. Não existem variáveis ocultas gerando viés.
2. **Suporte Comum (Positivity):** Todo tipo de cliente na base tinha uma probabilidade maior que zero e menor que um de receber o cupom (fato comprovado na análise de distribuição, onde aplicamos um *trimming* de probabilidades extremas).
3. **SUTVA:** O tratamento recebido por um cliente não afetou o comportamento de compra de outro.

## 7. Conclusão Gerencial
O impacto do cupom de desconto de 20% foi **superestimado** por uma leitura inicial ingênua. Os clientes que receberam a promoção não gastaram em média R$ 144,56 a mais *por causa do cupom*; R$ 95,70 desse montante era "dinheiro deixado na mesa" (eles gastariam de qualquer forma, por serem os clientes VIPs).

O **verdadeiro incremento causal no ticket médio por cliente foi de R$ 48,86** nos 30 dias seguintes (com altíssima segurança estatística, variando no máximo entre 46 e 50 reais). 

A magnitude do efeito (R$ ~49) é positiva, indicando que a campanha funcionou, mas a empresa deve agora calcular o ROI da ação. Se a margem de contribuição (lucro) sobre esses R$ 48,86 for menor que o custo do desconto cedido aos clientes, a campanha teve prejuízo. Recomenda-se para as próximas campanhas realizar testes A/B verdadeiramente aleatórios ou focar o desconto nos clientes da base que não são VIPs, para avaliar onde a elasticidade de resposta ao desconto é maior.
