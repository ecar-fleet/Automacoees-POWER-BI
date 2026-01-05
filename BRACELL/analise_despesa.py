import datetime

import config

dd = "01"
mm = datetime.datetime.now().strftime("%m")
aa = datetime.datetime.now().strftime("%y")

data_inicial = f"{dd}/{mm}/20{aa}"

pasta_download = r"C:\Users\Dell\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Manutenção\Despesas por Veículo"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador, relatorio="5132")
config.filtrar_data(navegador, data_inicial)
config.baixar_relatorio(driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, f"Analise de despesa por veiculo  {mm}-{aa}.xlsx")
config.renomear_arquivo(arquivo_baixado, f"Analise de despesa por veiculo  {mm}-{aa}.xlsx", pasta_download)