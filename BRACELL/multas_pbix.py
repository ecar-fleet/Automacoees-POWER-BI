import config

pasta_download = r"C:\Users\Dell\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Relatório de Multas"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador)
config.baixar_relatorio("3613", driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Relatório de Multas.xlsx")
config.renomear_arquivo(arquivo_baixado, "Relatório de Multas.xlsx", pasta_download)