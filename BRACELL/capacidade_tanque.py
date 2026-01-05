import config

pasta_download = r"c:\Users\DELL\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Capacidade Tanque"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador, relatorio="2227")
config.baixar_relatorio(driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Capacidade Tanque SP.xlsx")
config.renomear_arquivo(arquivo_baixado, "Capacidade Tanque SP.xlsx", pasta_download)