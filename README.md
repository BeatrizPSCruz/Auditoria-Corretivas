Este projeto automatiza a auditoria de ordens de serviço (OS) vindas do ERP, identificando inconsistências, falhas de preenchimento e erros de lógica de negócio em tempo real. Além da validação, o script gera indicadores de saúde da base de dados e um histórico de conformidade.  

Funcionalidades:
- Auditoria Automatizada: Valida campos obrigatórios, datas lógicas e regras de negócio específicas (ex: SIOF em ordens de emergência).
- Monitoramento de KPI: Calcula o Data Quality Score (DQS) a cada execução.
- Persistência de Histórico: Registra o DQS em um arquivo CSV, permitindo o acompanhamento da evolução da qualidade ao longo do tempo.
- Visualização: Gera automaticamente um gráfico de tendência (PNG) destacando o desempenho atual em relação à meta definida (95%).
- Relatório de Erros: Exporta um arquivo Excel contendo apenas as ordens de serviço que necessitam de intervenção humana.

Tecnologias Utilizadas:
- Python (Pandas para processamento, Matplotlib para visualização).
- Automação: Auditoria baseada em regras de negócio declarativas.
- Excel: Integração para entrada e saída de dados.

  <img width="3600" height="1800" alt="Evolucao_DQS" src="https://github.com/user-attachments/assets/ba6f31da-9072-45c8-99fc-de5f79b18121" />
