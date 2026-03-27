import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from deep_translator import GoogleTranslator

# Configurações
BASE_URL = "https://www.scamwarners.com/forum/"
START_URL = "https://www.scamwarners.com/forum/viewforum.php?f=6"

def traduzir_texto(texto):
    """Traduz o texto de inglês para português em blocos para evitar erros de limite."""
    try:
        # O tradutor tem um limite por requisição, cortamos se for muito grande
        if len(texto) > 4500:
            texto = texto[:4500]
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except Exception as e:
        print(f"\nErro na tradução: {e}")
        return texto # Retorna original se falhar

def extrair_conteudo_topico(scraper, url):
    try:
        time.sleep(random.uniform(1.5, 2.5))
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        elemento = soup.select_one("div.postbody div.content blockquote.uncited")
        
        if elemento:
            texto_en = elemento.get_text(strip=True)
            if texto_en: # Verifica se não está vazio
                return traduzir_texto(texto_en)
        return None
    except Exception as e:
        return None

def crawler_scamwarners(limite_linhas):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    resultados = []
    start_param = 0
    
    print(f"Iniciando coleta de {limite_linhas} registros válidos e traduzidos...")

    while len(resultados) < limite_linhas:
        url_paginacao = f"{START_URL}&start={start_param}"
        response = scraper.get(url_paginacao, timeout=15)
        
        if response.status_code != 200:
            print(f"\nErro ao acessar listagem ({response.status_code}).")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links_topicos = soup.find_all("a", class_="topictitle")
        
        if not links_topicos:
            break

        for link in links_topicos:
            if len(resultados) >= limite_linhas:
                break
            
            href = link.get('href').split('&sid=')[0]
            url_completa = BASE_URL + href.replace("./", "")
            
            # Tenta extrair e traduzir
            texto_pt = extrair_conteudo_topico(scraper, url_completa)
            
            # REGRA: Só adiciona se tiver conteúdo real
            if texto_pt and texto_pt != "Conteúdo não encontrado":
                resultados.append({
                    "Link Original": url_completa,
                    "Conteúdo do Golpe (Traduzido)": texto_pt
                })
                print(f"Progresso: {len(resultados)}/{limite_linhas} concluídos", end='\r')
            else:
                # Se estiver vazio, o loop continua buscando o próximo link automaticamente
                continue

        start_param += 50
        time.sleep(1)
        
    return resultados

def salvar_formatado(dados):
    df = pd.DataFrame(dados)
    nome_arquivo = "lojas_falsas_traduzido.xlsx"
    
    # Criar um escritor do Excel com formatação
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Golpes')
        
        # Ajustes estéticos básicos
        worksheet = writer.sheets['Golpes']
        # Ajusta largura das colunas
        worksheet.column_dimensions['A'].width = 40
        worksheet.column_dimensions['B'].width = 100
        
    print(f"\n\nSucesso! Arquivo '{nome_arquivo}' gerado com {len(df)} linhas válidas.")

if __name__ == "__main__":
    DADOS = crawler_scamwarners(150)
    if DADOS:
        salvar_formatado(DADOS)