import config

pasta_download = r"C:\Users\Dell\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Manutenção\Ordens de Serviço"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador, relatorio="2689")
config.baixar_relatorio(driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Ordens de Serviço.xlsx")
config.renomear_arquivo(arquivo_baixado, "Ordens de Serviço.xlsx", pasta_download)