from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
        
        
def fazer_login(usuario, senha):
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


def baixar_relatorio(pasta):
        chrome_options = Options()
        prefs = {
    "download.default_directory": pasta,  # pasta de download
    "download.prompt_for_download": False,       # não perguntar
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
        
        
        