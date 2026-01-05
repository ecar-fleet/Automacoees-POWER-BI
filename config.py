import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

USERNAME = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD") 

def criar_driver(pasta_download):
    import os

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    pasta_download = os.path.abspath(pasta_download)

    options = Options()
    prefs = {
        "download.default_directory": pasta_download,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)
        
        
def fazer_login(driver, usuario=USERNAME, senha=PASSWORD):
        wait = WebDriverWait(driver, 10)
        driver.get("https://sofitview.com.br/#/login")
        print("2.1. Acessando página de login...")
        campo_usuario = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Informe seu usuário']")))
        campo_usuario.send_keys(usuario)
        campo_senha = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        campo_senha.send_keys(senha)
        botao_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fazer login')]")))
        botao_login.click()
        print("Login realizado.")

        wait.until(EC.url_contains("/client"))
        print("2.2. Login bem-sucedido, redirecionado para a página do cliente.")


def baixar_relatorio(relatorio, driver):
      wait = WebDriverWait(driver, 60)
      driver.get(f"https://sofitview.com.br/#/client/reports/{relatorio}")
      botao_download = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title = 'Exportar como planilha']")))
      botao_download.click()

def renomear_arquivo(nome_antigo, nome_novo, pasta_download):
    import os
    import time

    caminho_antigo = os.path.join(pasta_download, nome_antigo)
    caminho_novo = os.path.join(pasta_download, nome_novo)

    # Espera até o arquivo ser baixado completamente
    while not os.path.exists(caminho_antigo):
        time.sleep(1)

    # Se o arquivo de destino já existir, remove para sobrescrever
    if os.path.exists(caminho_novo):
        os.remove(caminho_novo)
        print(f"Arquivo antigo '{nome_novo}' removido.")

    os.rename(caminho_antigo, caminho_novo)
    print(f"Arquivo renomeado para {nome_novo}")


def encontrar_arquivo_baixado(pasta_download, prefixo, extensao=".xlsx", timeout=60, nome_ignorar=None):
    """Encontra o arquivo mais recente que começa com o prefixo especificado."""
    import glob
    import time

    padrao = os.path.join(pasta_download, f"{prefixo}*{extensao}")
    tempo_inicial = time.time()
    
    # Nome do arquivo base que deve ser ignorado (o arquivo antigo sem data)
    if nome_ignorar is None:
        nome_ignorar = f"{prefixo}{extensao}"

    while True:
        arquivos = glob.glob(padrao)
        # Filtra arquivos temporários (.crdownload, .tmp) e o arquivo base sem data
        arquivos = [f for f in arquivos if not f.endswith(('.crdownload', '.tmp'))]
        arquivos = [f for f in arquivos if os.path.basename(f) != nome_ignorar]
        
        if arquivos:
            # Retorna o arquivo mais recente
            arquivo_mais_recente = max(arquivos, key=os.path.getmtime)
            return os.path.basename(arquivo_mais_recente)
        
        if time.time() - tempo_inicial > timeout:
            raise TimeoutError(f"Arquivo com prefixo '{prefixo}' não encontrado em {timeout} segundos.")
        
        time.sleep(1)
        
        
        