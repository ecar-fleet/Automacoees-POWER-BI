"""
Automação: anexar o CRLV (PDF) de cada veículo no Sofit View.

Percorre TODAS as subpastas de:
    C:\\Users\\DELL\\Ecarfleet\\Intranet - 13. CRLV's Bracell
e, para cada arquivo "CRLV - <ano> - <PLACA>.pdf":
    1. Extrai a placa do nome do arquivo (ex.: "GJO2E21").
    2. Faz login no Sofit (uma vez) e abre a busca com escopo de veículo
       (#/client/search?query=<placa>&tables=["vehicle"]). Havendo um único
       resultado, a página redireciona sozinha para #/client/vehicles/<id>.
    3. Abre a edição da documentação: #/client/vehicles/<id>/edit?step=documentation.
    4. No campo "Arquivo do CRLV:", clica em "Selecionar arquivo" para abrir o
       modal "Anexar arquivo", envia o PDF, clica em "Enviar" (uploadFile) e
       depois "Salvar". O sucesso é confirmado pelo link "Visualizar arquivo
       atual" surgir no campo (anexo real) e pela saída da tela de edição.
    5. Move o PDF processado para a pasta "crlv's anexadas".

A pasta "crlv's anexadas" também serve de marcador de "já feito": ao rodar
de novo, os PDFs que já foram movidos não são reprocessados.

Fluxo e seletores foram confirmados inspecionando o site ao vivo.

Reutiliza credenciais (.env -> LOGIN / PASSWORD) e o driver do config.py,
exatamente como os demais scripts da pasta BRACELL.

Uso:
    python anexar_crlv.py
"""

import os
import re
import shutil
import sys
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO / SELETORES  (ajuste aqui se algum elemento mudar no site)
# ---------------------------------------------------------------------------
PASTA_BASE = r"C:\Users\DELL\Ecarfleet\Intranet - 13. CRLV's Bracell"
PASTA_DESTINO = os.path.join(PASTA_BASE, "crlv's anexadas")
PASTA_ERRO = os.path.join(PASTA_BASE, "crlv erro")

TIMEOUT = 30  # segundos de espera máxima para cada elemento

URL_LOGIN = "https://sofitview.com.br/#/login"
URL_VEICULOS = "https://sofitview.com.br/#/client/vehicles"
# Busca com escopo de veículo. tables=["vehicle"] (URL-encoded) faz a página
# redirecionar direto para o veículo quando há um único resultado.
URL_BUSCA = "https://sofitview.com.br/#/client/search?query={placa}&tables=%5B%22vehicle%22%5D"
# Edição da documentação do veículo.
URL_EDIT = "https://sofitview.com.br/#/client/vehicles/{vid}/edit?step=documentation"

# Botão "Selecionar arquivo" (a "pasta") do campo "Arquivo do CRLV:".
# Clicá-lo abre o modal "Anexar arquivo". O envio direto no input[type=file]
# do campo NÃO funciona — o componente só registra o anexo via esse modal.
SELETOR_BTN_SELECIONAR = (
    "//div[@title='Arquivo do CRLV']/ancestor::div[contains(@class,'form-group')][1]"
    "//button[@title='Selecionar arquivo']"
)
# input[type=file] dentro do modal "Anexar arquivo".
SELETOR_MODAL_FILE = "//div[contains(@class,'bs-modal')]//input[@type='file']"
# Botão "Enviar" do modal (faz o upload do arquivo).
SELETOR_UPLOAD = "//button[@name='uploadFile']"
# Link "Visualizar arquivo atual" do campo CRLV: só aparece quando há arquivo
# anexado — é a confirmação REAL de que o upload deu certo.
SELETOR_CRLV_LINK = (
    "//div[@title='Arquivo do CRLV']/ancestor::div[contains(@class,'form-group')][1]"
    "//a[contains(@class,'file-link')]"
)
# Botão "Salvar" do formulário de edição.
SELETOR_SALVAR = "//button[@type='submit' and @title='Salvar']"

# Segundos de espera para o dropzone ler o arquivo antes de clicar em "Enviar".
ESPERA_LEITURA_ARQUIVO = 2


# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------
def extrair_placa(caminho_pdf):
    """De 'CRLV - 2026 - GJO2E21.pdf' retorna 'GJO2E21'.

    Reconhece placa antiga (ABC1234) e Mercosul (ABC1D23). Se nenhum padrão
    casar, usa o último segmento do nome como fallback.
    """
    nome = os.path.splitext(os.path.basename(caminho_pdf))[0].upper()
    m = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", nome)
    if m:
        return m.group(0)
    partes = [p.strip() for p in nome.split(" - ") if p.strip()]
    placa = partes[-1] if partes else nome
    return placa.replace("-", "").replace(" ", "")


def listar_pdfs():
    """Lista todos os PDFs nas subpastas, ignorando as pastas de saída."""
    pdfs = []
    ignorar = {os.path.abspath(PASTA_DESTINO), os.path.abspath(PASTA_ERRO)}
    for raiz, dirs, arquivos in os.walk(PASTA_BASE):
        dirs[:] = [
            d for d in dirs
            if os.path.abspath(os.path.join(raiz, d)) not in ignorar
        ]
        for nome in arquivos:
            if nome.lower().endswith(".pdf"):
                pdfs.append(os.path.join(raiz, nome))
    return sorted(pdfs)


def mover_para(caminho_pdf, pasta):
    """Move o PDF para 'pasta' (cria se preciso, sem sobrescrever)."""
    os.makedirs(pasta, exist_ok=True)
    base = os.path.basename(caminho_pdf)
    destino = os.path.join(pasta, base)
    if os.path.exists(destino):
        nome, ext = os.path.splitext(base)
        i = 1
        while os.path.exists(destino):
            destino = os.path.join(pasta, f"{nome} ({i}){ext}")
            i += 1
    shutil.move(caminho_pdf, destino)


def login(driver):
    """Login no Sofit reutilizando as credenciais do config.py (.env)."""
    wait = WebDriverWait(driver, TIMEOUT)
    driver.get(URL_LOGIN)
    print("Acessando pagina de login...")
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Informe seu usuário']")
        )
    ).send_keys(config.USERNAME)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(config.PASSWORD)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fazer login')]"))
    ).click()
    wait.until(EC.url_contains("/client"))
    print("Login realizado com sucesso.")


def buscar_veiculo(driver, wait, placa):
    """Abre o veículo a partir da placa e retorna o id.

    Navega direto para a busca com escopo de veículo
    (#/client/search?query=<placa>&tables=["vehicle"]); havendo um único
    resultado, a página redireciona sozinha para #/client/vehicles/<id>.
    É mais robusto que digitar na caixa de busca (que depende do escopo).
    """
    driver.get(URL_BUSCA.format(placa=placa))
    # driver.get só troca o fragmento (#) e NÃO recarrega a página; o redirect
    # da rota de busca só dispara num carregamento completo — então forçamos o
    # reload para garantir o redirecionamento ao veículo.
    driver.execute_script("window.location.reload();")
    try:
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: re.search(r"/client/vehicles/(\d+)", d.current_url)
        )
    except TimeoutException:
        raise TimeoutException(
            f"Busca da placa {placa} nao redirecionou para um veiculo "
            f"(URL: {driver.current_url}). Pode nao existir ou ter varios resultados."
        )
    return re.search(r"/client/vehicles/(\d+)", driver.current_url).group(1)


def anexar_e_salvar(driver, wait, vid, caminho_abs):
    """Abre a edição da documentação, anexa o PDF do CRLV (via modal) e salva."""
    driver.get(URL_EDIT.format(vid=vid))
    wait.until(EC.url_contains("edit?step=documentation"))

    # 1) Abre o modal "Anexar arquivo" pelo botão da pasta do campo CRLV.
    btn = wait.until(EC.presence_of_element_located((By.XPATH, SELETOR_BTN_SELECIONAR)))
    driver.execute_script("arguments[0].click();", btn)

    # 2) Envia o PDF ao input[type=file] do modal e dá um tempo para o dropzone
    #    ler o arquivo (se clicar em "Enviar" cedo demais, sobe vazio).
    file_input = wait.until(EC.presence_of_element_located((By.XPATH, SELETOR_MODAL_FILE)))
    file_input.send_keys(caminho_abs)
    time.sleep(ESPERA_LEITURA_ARQUIVO)

    # 3) Clica em "Enviar" (uploadFile).
    enviar = wait.until(EC.element_to_be_clickable((By.XPATH, SELETOR_UPLOAD)))
    driver.execute_script("arguments[0].click();", enviar)

    # 4) Confirmação REAL: o modal fecha e o link do arquivo aparece no campo
    #    CRLV. Sem isso, tratamos como falha (o arquivo não será movido).
    WebDriverWait(driver, TIMEOUT).until(
        EC.invisibility_of_element_located((By.XPATH, SELETOR_MODAL_FILE))
    )
    WebDriverWait(driver, TIMEOUT).until(
        EC.visibility_of_element_located((By.XPATH, SELETOR_CRLV_LINK))
    )
    print("   CRLV anexada (upload confirmado).")

    # 5) Salva o veículo. Sucesso = sai da tela de edição (redireciona).
    salvar = wait.until(EC.element_to_be_clickable((By.XPATH, SELETOR_SALVAR)))
    driver.execute_script("arguments[0].click();", salvar)
    WebDriverWait(driver, TIMEOUT).until(lambda d: "/edit" not in d.current_url)
    print("   [OK] Veiculo salvo.")


def processar_pdf(driver, caminho_pdf):
    """Fluxo completo para um PDF, a partir da placa no nome do arquivo."""
    wait = WebDriverWait(driver, TIMEOUT)
    placa = extrair_placa(caminho_pdf)
    print(f"\n>>> Processando {os.path.basename(caminho_pdf)} (placa: {placa})")

    # Se a SPA tiver deslogado, refaz o login.
    if "/login" in driver.current_url:
        login(driver)

    vid = buscar_veiculo(driver, wait, placa)
    anexar_e_salvar(driver, wait, vid, os.path.abspath(caminho_pdf))


# ---------------------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    # Evita UnicodeEncodeError no console do Windows ao imprimir nomes/erros.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if not config.USERNAME or not config.PASSWORD:
        print("ERRO: credenciais nao encontradas. Defina LOGIN e PASSWORD no .env.")
        return

    if not os.path.isdir(PASTA_BASE):
        print(f"ERRO: pasta base nao encontrada: {PASTA_BASE}")
        return

    pdfs = listar_pdfs()
    print(f"Encontrados {len(pdfs)} PDF(s) para processar em '{PASTA_BASE}'.")
    if not pdfs:
        return

    driver = config.criar_driver(PASTA_BASE)
    sucesso, falha = [], []
    try:
        driver.maximize_window()
        login(driver)
        driver.get(URL_VEICULOS)  # contexto inicial (escopo de busca = Veículos)

        for caminho in pdfs:
            try:
                processar_pdf(driver, caminho)
                mover_para(caminho, PASTA_DESTINO)
                sucesso.append(os.path.basename(caminho))
                print(f"   -> movido para '{os.path.basename(PASTA_DESTINO)}'.")
            except Exception as e:
                falha.append((os.path.basename(caminho), str(e).splitlines()[0]))
                print(f"   [FALHA] {str(e).splitlines()[0]}")
                # Screenshot para depuração e move o PDF para a pasta de erro.
                try:
                    placa = extrair_placa(caminho)
                    os.makedirs(PASTA_ERRO, exist_ok=True)
                    driver.save_screenshot(os.path.join(PASTA_ERRO, f"_erro_{placa}.png"))
                except Exception:
                    pass
                try:
                    mover_para(caminho, PASTA_ERRO)
                    print(f"   -> movido para '{os.path.basename(PASTA_ERRO)}'.")
                except Exception as e2:
                    print(f"   (nao foi possivel mover para erro: {e2})")
    finally:
        driver.quit()

    print("\n================ RESUMO ================")
    print(f"Sucesso: {len(sucesso)}")
    print(f"Falhas:  {len(falha)}")
    for nome, err in falha:
        print(f"  - {nome}: {err}")


if __name__ == "__main__":
    main()
