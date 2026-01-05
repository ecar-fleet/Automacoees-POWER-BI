import config

pasta_download = r"C:\Users\Dell\Ecarfleet\Intranet - AUTOMATIZAÇÃO POWER BI\Bracell - SP\Manutenção\Valores Contestados"

navegador = config.criar_driver(pasta_download)
config.fazer_login(driver=navegador)
config.baixar_relatorio("5791", driver=navegador)

# Encontra o arquivo baixado (que tem a data no nome) e renomeia
arquivo_baixado = config.encontrar_arquivo_baixado(pasta_download, "Valores Contestados  SP.xlsx")
config.renomear_arquivo(arquivo_baixado, "Valores Contestados  SP.xlsx", pasta_download)