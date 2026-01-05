import config

pasta_download = r"C:\Users\DELL\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Filiais"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador, relatorio="2722")
config.baixar_relatorio(driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Filiais SP.xlsx")
config.renomear_arquivo(arquivo_baixado, "Filiais SP.xlsx", pasta_download)