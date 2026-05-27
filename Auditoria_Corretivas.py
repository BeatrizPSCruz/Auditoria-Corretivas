import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates


BD_Falhas = "BD_Analise_de_Falhas.xlsx"
BD_OS = "BD_Auditoria_Corretivas.xlsx"



df_OS = pd.read_excel(BD_OS, keep_default_na=False)
df_Falhas = pd.read_excel(BD_Falhas, keep_default_na=False)

colunas_para_trazer = ['Nome da Ordem de Serviço', 'Falha', 'Causa', 'Resolução', 'Comentários']
df_final = pd.merge(
    df_OS, 
    df_Falhas[colunas_para_trazer], 
    left_on='Ordem de Servico', 
    right_on='Nome da Ordem de Serviço', 
    how='left'
)

cols_data = ['Data da Falha', 'Data Real Inicial de Execução da OS', 'Data Real Final de Execução da OS']
for col in cols_data:
    df_final[col] = pd.to_datetime(df_final[col], errors='coerce')

status_excluidos = ['Cancelado', 'Não Liberado', 'Liberado', 'Execução Parcial', 'Em Retenção']

df_final = df_final[~df_final['Status'].isin(status_excluidos)].copy()
df_final = df_final[df_final['Tipo de OS'] == 'CORRECTIVE'].copy()

df_final['Codigo SIOF'] = df_final['Codigo SIOF'].replace(["NA", "na"], "SEM SIOF" )
df_final['COSE'] = df_final['COSE'].replace(["NA", "na"], "SEM COSE" )

df_final = df_final[~df_final['Ordem de Servico'].str.contains('.ROTA', na=False)].copy()

hoje = pd.Timestamp(dt.datetime.today().date())
SubtipoStatus = ['Planejado', 'Emergência']

def auditar_linha(row):
    lista_erros = []
    
    descricao = str(row.get('Descricao da Ordem de Servico', '')).strip()
    subtipo = str(row.get(' Subtipo de OS', '')).strip()
    data_falha = row.get('Data da Falha')
    segmento = str(row.get('Segmento de Contexto', '')).strip()
    falha_ou_defeito = str(row.get('Falha ou Defeito', '')).strip()
    falha = str(row.get('Falha', '')).strip()
    Ativo = str(row.get('Numero do Ativo', '')).strip()
    causa = str(row.get('Causa', '')).strip()
    resolucao = str(row.get('Resolução', '')).strip()
    comentario = str(row.get('Comentários', '')).strip()
    local_exec = str(row.get('Local Físico da Execução da OS', '')).strip()
    depto = str(row.get('Departamento da Ordem de Serviço', '')).strip()
    data_ini = row.get('Data Real Inicial de Execução da OS')
    data_fim = row.get('Data Real Final de Execução da OS')
    siof = str(row.get('Codigo SIOF', '')).strip()
    TipoOcorrencia = str(row.get('Tipo de Ocorrencia', '')).strip()
    COSE = str(row.get('COSE', '')).strip()
    MetaDeFalha = str(row.get('Meta de Falha', '')).strip()

    

    # Validações de texto
    if descricao in ["", "nan", "None"]: lista_erros.append("Descrição em branco")
    if subtipo not in SubtipoStatus: lista_erros.append("Subtipo incorreto")
    if subtipo == "Emergência" and siof in ["", "nan", "None"]: lista_erros.append("SIOF em branco")
    if TipoOcorrencia in ["", "nan", "None"]: lista_erros.append("Tipo de Ocorrência em branco")
    if TipoOcorrencia in ['FURTO', 'VANDALISMO'] and COSE in ["", "nan", "None"]: lista_erros.append("COSE em branco")
    if TipoOcorrencia in ['EM APURACAO']: lista_erros.append("Tipo de Ocorrência em apuração")
    if local_exec in ["", "nan", "None"]: lista_erros.append("Local Físico da Execução em branco")
    if depto in ["", "nan", "None"]: lista_erros.append("Departamento Responsavel em branco")

    if segmento in ["", "nan", "None"]: lista_erros.append("Segmento de Contexto em branco")
    elif segmento != "OCORRENCIA": lista_erros.append("Segmento de Contexto incorreto")

    if ".ROTA" in Ativo.upper(): lista_erros.append("OS criada em um ativo de rota")
    
    # Validações de Falha ou Defeito
    if falha_ou_defeito in ["", "nan", "None"]: lista_erros.append("Campo 'Falha ou Defeito' em branco")
    if falha in ["", "nan", "None"]: lista_erros.append("Campo 'Falha' em branco")
    if causa in ["", "nan", "None"]: lista_erros.append("Campo 'Causa' em branco")
    if resolucao in ["", "nan", "None"]: lista_erros.append("Campo 'Resolução' em branco")
    if comentario in ["", "nan", "None"]: lista_erros.append("Campo 'Comentários' em branco")
    if MetaDeFalha in ["", "nan", "None"]: lista_erros.append("Meta de Falha em branco")

    # Validações de Data
    if pd.isna(data_falha):
        lista_erros.append("Data da falha em branco")
    elif data_falha > hoje:
        lista_erros.append("Data da falha posterior a data de hoje")

    if pd.isna(data_ini): lista_erros.append("Campo 'Data Real Inicial da Execução da OS' em branco")
    if pd.isna(data_fim): lista_erros.append("Campo 'Data Real Final da Execução da OS' em branco")

    # Comparações entre datas
    if pd.notna(data_ini) and pd.notna(data_fim):
        if data_ini > data_fim: lista_erros.append("Data Inicial posterior à Data Final de Execução da OS")
        if data_ini > hoje: lista_erros.append("Data Inicial da Execução da OS posterior à hoje")
        if data_fim > hoje: lista_erros.append("Data Final da Execução da OS posterior à hoje")
        if pd.notna(data_falha) and data_ini < data_falha:
            lista_erros.append("Data Inicial da Execução da OS anterior à data da falha")

    return "; ".join(lista_erros) if lista_erros else "Ok"

df_final['Auditoria_Final'] = df_final.apply(auditar_linha, axis=1)

total_registros = len(df_final)
registros_ok = len(df_final[df_final['Auditoria_Final'] == 'Ok'])

dqs = (registros_ok / total_registros) * 100 if total_registros > 0 else 0
print(f"Data Quality Score: {dqs:.2f}%")

novo_log = {
    'Data_Execucao': [dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    'Total_Registros': [total_registros],
    'Registros_Validos': [registros_ok],
    'DQS': [round(dqs, 2)]
}

df_log = pd.DataFrame(novo_log)


arquivo_log = "Historico_DQS.csv"

if not os.path.exists(arquivo_log):
    df_log.to_csv(arquivo_log, index=False)
else:
    df_log.to_csv(arquivo_log, mode='a', header=False, index=False)




# ---------------------------------------- GERAR ARQUIVO ----------------------------------------

df_final = df_final.drop(columns=['Nome da Ordem de Serviço', 'Número do Projeto', 'Nome do Projeto', 'Nome da Tarefa', 'Número da Tarefa',
                                  'Descrição do Item', 'Descricao Longa do Item', 'Item', 'KM do Ramal do Ativo', 'Linha/ CKT/ FO do Ativo',
                                  'AMV do Ativo', 'Classe da Categoria do Ativo', 'Nome da Definição de Trabalho', 'UA para Contabilização de Recurso de Projeto'],
                                  errors='ignore')

df_final = df_final[df_final['Auditoria_Final'] != 'Ok'].copy()

df_final.to_excel("DF_Final.xlsx", index=False)



# ---------------------------------------- GERAR GRÁFICO ----------------------------------------
plt.style.use('seaborn-v0_8-whitegrid')

df_hist = pd.read_csv("Historico_DQS.csv")
df_hist['Data_Execucao'] = pd.to_datetime(df_hist['Data_Execucao'])

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(df_hist['Data_Execucao'], df_hist['DQS'], marker='o', 
        linestyle='-', color='#2c3e50', linewidth=2.5, markersize=8, label='DQS Real')

meta = 95
ax.axhline(y=meta, color='#e74c3c', linestyle='--', linewidth=2, label=f'Meta ({meta}%)')

ax.fill_between(df_hist['Data_Execucao'], df_hist['DQS'], meta, 
                where=(df_hist['DQS'] < meta), color='#ff7675', alpha=0.3, interpolate=True)

ax.set_title('Evolução do Data Quality Score (DQS)', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('Score (%)', fontsize=12)
ax.set_ylim(0, 105)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=30)) 

ax.legend(loc='lower right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig("Evolucao_DQS.png", dpi=300) 
plt.show()





print("Processamento concluído com sucesso!")