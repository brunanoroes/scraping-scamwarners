Web Scraping: ScamWarners (Romance Scams)
Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC). O objetivo é a coleta automatizada de relatos de golpes sentimentais (romance scams) do fórum ScamWarners, permitindo a análise de dados e padrões de comportamento desses golpes.

Funcionalidades
Navegação Inteligente: Percorre as páginas do fórum via parâmetros de paginação (start=50, 100...).

Extração Seletiva: Coleta apenas os textos contidos em blockquote.uncited, focando no conteúdo real do golpe.

Tradução Automática: Traduz os relatos de Inglês para Português em tempo real usando a API do Google (via deep-translator).

Garantia de Qualidade: O script ignora tópicos sem conteúdo, garantindo que o dataset final tenha exatamente o número de registros válidos solicitado.

Anti-Bloqueio: Utiliza a biblioteca cloudscraper para contornar proteções 403 (Cloudflare) e emular um navegador real.

Exportação Formatada: Gera um arquivo .xlsx (Excel) com colunas ajustadas para leitura.

Tecnologias Utilizadas
Python 3.13

Pandas: Manipulação de dados e criação do DataFrame.

BeautifulSoup4: Parsing de HTML.

Cloudscraper: Bypass de proteções e requisições HTTP.

Deep-Translator: Tradução automática de idiomas.

Openpyxl: Mecanismo para escrita de arquivos Excel.

Pré-requisitos
Antes de rodar o script, você precisará instalar as dependências. No terminal, utilize o comando:

PowerShell
python -m pip install cloudscraper pandas openpyxl beautifulsoup4 deep-translator
📂 Como Usar
Clone o repositório ou baixe o arquivo scraping.py.

Abra o terminal na pasta do projeto.

Execute o script com o comando:

PowerShell
python scraping.py
O arquivo scamwarners_traduzido.xlsx será gerado na mesma pasta ao final do processo.

 Notas Éticas
Este scraper foi construído para fins estritamente acadêmicos. Ele respeita o servidor através de delays aleatórios (time.sleep) para evitar sobrecarga no site de origem.