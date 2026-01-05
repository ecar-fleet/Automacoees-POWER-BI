import config

pasta_download = r"C:\Users\Dell\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Despesas da Frota"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador)
config.baixar_relatorio("5890", driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Despesa da Frota Bracell  SP.xlsx")
config.renomear_arquivo(arquivo_baixado, "Despesa da Frota Bracell  SP.xlsx", pasta_download)