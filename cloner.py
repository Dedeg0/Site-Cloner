import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import asyncio
import aiohttp
import logging
import shutil
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
from zipfile import ZipFile
import time

# Configurações de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Verifica e instala o Selenium automaticamente
def ensure_selenium():
    try:
        from selenium import webdriver
    except ImportError:
        logging.info("Selenium não encontrado. Instalando...")
        subprocess.check_call(["pip", "install", "selenium"])
        from selenium import webdriver  # Importa novamente após a instalação

# Função para criar diretório local
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Função para salvar arquivos
async def save_file(session, url, output_dir):
    try:
        parsed_url = urlparse(url)
        subdir = 'outros'
        if parsed_url.path.endswith(('.css', '.js')):
            subdir = parsed_url.path.split('.')[-1]
        elif parsed_url.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
            subdir = 'imagens'

        full_dir = os.path.join(output_dir, subdir)
        create_directory(full_dir)

        async with session.get(url) as response:
            if response.status == 200:
                filename = os.path.basename(parsed_url.path)
                filepath = os.path.join(full_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(await response.read())
                logging.info(f"Arquivo salvo: {filepath}")
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo {url}: {e}")

# Função de autenticação usando Selenium
def authenticate_with_selenium(login_url, username, password):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    service = Service(executable_path='chromedriver')  # Atualize o caminho do chromedriver

    driver = webdriver.Chrome(service=service, options=options)
    try:
        logging.info("Acessando a página de login...")
        driver.get(login_url)

        # Localizar campos de login e senha (ajuste os seletores conforme necessário)
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        logging.info("Login realizado com sucesso.")
        cookies = driver.get_cookies()
        return cookies
    finally:
        driver.quit()

# Função de compactação
def zip_directory(directory):
    zip_file = f"{directory}.zip"
    with ZipFile(zip_file, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=directory)
                zipf.write(file_path, arcname=arcname)
    logging.info(f"Diretório compactado em: {zip_file}")

# Função de scraping principal
def clone_page(url, use_selenium=False, username=None, password=None):
    ensure_selenium()

    # Extrair nome do site para criar pasta automaticamente
    parsed_url = urlparse(url)
    site_name = parsed_url.netloc.replace("www.", "")
    output_dir = os.path.join(os.getcwd(), site_name)
    create_directory(output_dir)

    # Verificação de login
    cookies = None
    if use_selenium and username and password:
        cookies = authenticate_with_selenium(url, username, password)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    async def fetch_content():
        async with aiohttp.ClientSession(headers=headers, cookies={cookie['name']: cookie['value'] for cookie in cookies} if cookies else None) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    page_content = await response.text()
                    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
                        f.write(page_content)
                    logging.info("HTML principal salvo.")
                    return page_content, session
                else:
                    logging.error(f"Erro ao acessar a página: {response.status}")

    async def fetch_assets(page_content):
        async with aiohttp.ClientSession(headers=headers, cookies={cookie['name']: cookie['value'] for cookie in cookies} if cookies else None) as session:
            soup = BeautifulSoup(page_content, "html.parser")

            # Captura links para recursos estáticos
            assets = []
            for tag, attr in [("img", "src"), ("link", "href"), ("script", "src")]:
                for element in soup.find_all(tag):
                    url_asset = element.get(attr)
                    if url_asset:
                        full_url = urljoin(url, url_asset)
                        assets.append(full_url)

            with tqdm(total=len(assets), desc="Baixando recursos", unit="arquivo") as pbar:
                tasks = [save_file(session, asset_url, output_dir) for asset_url in assets]
                for task in asyncio.as_completed(tasks):
                    await task
                    pbar.update(1)

    async def main():
        page_content, session = await fetch_content()
        if page_content:
            await fetch_assets(page_content)

    asyncio.run(main())

    # Compacta o diretório após o download
    zip_directory(output_dir)

# Interface do usuário
def main():
    print("--- Clonador de Páginas Web ---")
    url = input("Digite a URL da página: ").strip()
    use_selenium = input("A página requer login? (s/n): ").strip().lower() == 's'

    username = password = None
    if use_selenium:
        username = input("Digite o usuário: ").strip()
        password = input("Digite a senha: ").strip()

    start_time = time.time()
    clone_page(url, use_selenium, username, password)
    end_time = time.time()
    logging.info(f"Tempo total de execução: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()
