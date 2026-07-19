# scraping-scamwarners — Coleta de Relatos de Golpes do Fórum ScamWarners

**Artigo relacionado:** *VeritaPlugin: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook* — Universidade Federal Fluminense (UFF)

**Resumo do artigo.** A Engenharia Social em redes sociais explora vulnerabilidades para
iludir usuários, tornando defesas técnicas tradicionais insuficientes. Este trabalho
apresenta o VeritaPlugin, uma extensão de navegador que detecta fraudes no Facebook por
meio de um pipeline híbrido BERTimbau, RAG determinístico e GPT-4o. A arquitetura opera em
conformidade com a LGPD e o resultado apresenta ao usuário a categoria do golpe,
enquadramento legal e ações recomendadas. Para calibração, foi construído e disponibilizado
o dataset BrScamsFacebook, com 450 instâncias de golpes reais do contexto brasileiro. Na
avaliação técnica, o classificador obteve F1-macro de 0,763 ± 0,034 na validação cruzada
k=5, superando o baseline.

**Resumo do artefato.** Este repositório implementa o **coletor automatizado de relatos de
golpes do fórum [ScamWarners](https://www.scamwarners.com/)**, uma das seis fontes externas
que compõem o dataset **BrScamsFacebook**. O ScamWarners é um fórum público em que vítimas
e voluntários documentam golpes recebidos, reproduzindo na íntegra o texto das mensagens
fraudulentas — material valioso para treinar um classificador, mas disponível apenas em
inglês e sem estrutura de dados. O script resolve os três obstáculos práticos dessa coleta:
percorre a paginação do fórum, extrai seletivamente **apenas o texto do golpe** (o bloco
`blockquote.uncited`, que isola a mensagem original do comentário do relator) e o traduz
para o português em tempo real. A saída é um `.xlsx` com o link de origem e o conteúdo
traduzido, permitindo rastrear cada instância até seu tópico original. As fontes *Externo
1*, *Externo 5* e *Externo 7* do BrScamsFacebook foram produzidas com este código.

**Artefato principal:** [VeritaPlugin](https://github.com/brunanoroes/VeritaPlugin)
**Autora:** Bruna Norões — brunanoroes@id.uff.br

---

# Estrutura do readme.md

Este README segue os requisitos mínimos do Comitê Técnico de Artefatos do SBSeg 2026:

| Seção | Conteúdo |
|---|---|
| **Título projeto** | Identificação do artefato, vínculo com o artigo e resumo |
| **Estrutura do readme.md** | Esta seção — mapa do documento e organização do repositório |
| **Selos Considerados** | Selos pleiteados na avaliação |
| **Informações básicas** | Ambiente de execução, funcionamento do coletor e parâmetros |
| **Dependências** | Versões de linguagem, bibliotecas e serviços de terceiros |
| **Preocupações com segurança** | Ética de coleta, conteúdo malicioso e dependência de site externo |
| **Instalação** | Passo a passo para preparar o ambiente |
| **Teste mínimo** | Execução reduzida que demonstra o funcionamento |
| **Experimentos** | Papel deste repositório na composição do dataset |
| **LICENSE** | Licença do artefato |

## Organização do repositório

```
scraping-scamwarners/
├── scraping.py                     # Coletor: paginação, extração e tradução
├── scamwarners_romantico.xlsx      # Saída — relatos de golpes de relacionamento
├── lojas_falsas_traduzido.xlsx     # Saída — relatos de lojas virtuais falsas
├── financeiro_traduzido.xlsx       # Saída — relatos de golpes financeiros
├── LICENSE
└── Readme.md
```

As três planilhas correspondem a execuções distintas do script, cada uma apontando para um
subfórum diferente do ScamWarners (constante `START_URL`), e alimentam categorias
diferentes do BrScamsFacebook.

> **Nota sobre o estado do código.** O script versionado está configurado para o subfórum
> `f=6` e grava em `lojas_falsas_traduzido.xlsx`. As demais planilhas foram geradas
> alterando `START_URL` e o nome do arquivo de saída, conforme descrito em *Informações
> básicas*.

---

# Selos Considerados

Os selos considerados são: **Artefatos Disponíveis (SeloD)** e **Artefatos Funcionais
(SeloF)**.

| Selo | Onde é atendido neste README |
|---|---|
| **Disponíveis (D)** | Repositório público e estável no GitHub, com este README e licença MIT |
| **Funcionais (F)** | Seções *Dependências* (com versões), *Informações básicas* (ambiente), *Instalação* e *Teste mínimo* |

> Este repositório documenta a **origem de parte dos dados** do artefato principal
> [VeritaPlugin](https://github.com/brunanoroes/VeritaPlugin). Ele não sustenta uma
> reivindicação quantitativa própria — ver *Experimentos*.

---

# Informações básicas

## Ambiente de execução

| Item | Especificação |
|---|---|
| Sistema operacional | Windows 11 (também validado em Ubuntu 22.04 LTS) |
| Python | 3.13 (compatível com 3.10+) |
| Rede | **Necessária** — acessa o ScamWarners e a API de tradução do Google |
| GPU | Não necessária |

## Requisitos de hardware

| Recurso | Mínimo |
|---|---|
| CPU | 2 núcleos x86-64 |
| RAM | 512 MB |
| Disco | 100 MB (dependências) + < 5 MB (saída) |
| Banda | ≈ 50 MB para uma coleta de 150 registros |
| Tempo | ≈ 15–20 minutos para 150 registros (dominado pelos *delays* de cortesia) |

## Como o coletor funciona

```
START_URL (subfórum)
      │
      ▼
 Percorre a listagem via parâmetro de paginação (start=0, 50, 100, ...)
      │
      ▼
 Para cada link de tópico (a.topictitle):
      │
      ├── aguarda 1,5–2,5 s (delay aleatório de cortesia)
      ├── requisita a página do tópico via cloudscraper
      ├── extrai div.postbody div.content blockquote.uncited
      │      └── isola o texto do GOLPE, não o comentário do relator
      ├── se vazio → descarta e segue para o próximo
      └── traduz EN → PT (deep-translator / Google), truncando em 4.500 caracteres
      │
      ▼
 Acumula até atingir o limite de registros VÁLIDOS solicitado
      │
      ▼
 Exporta .xlsx com colunas "Link Original" e "Conteúdo do Golpe (Traduzido)"
```

### Decisões de projeto relevantes

| Decisão | Motivo |
|---|---|
| Seletor `blockquote.uncited` | Isola o **texto original do golpe**, descartando a narrativa e os comentários do usuário que reportou. Sem isso, o dataset conteria opinião de terceiros em vez do material fraudulento |
| Descarte de tópicos vazios | Garante que o arquivo final tenha **exatamente** o número de registros válidos solicitado, em vez de linhas em branco |
| `cloudscraper` em vez de `requests` | O fórum está atrás de proteção Cloudflare, que responde 403 a requisições HTTP simples |
| *Delay* aleatório de 1,5–2,5 s | Evita sobrecarregar o servidor de origem — ver *Preocupações com segurança* |
| Truncamento em 4.500 caracteres | A API de tradução tem limite por requisição; textos maiores falhariam |
| Fallback no erro de tradução | Se a tradução falhar, o texto original em inglês é preservado em vez de perder o registro |

## Parâmetros configuráveis

| Local | Constante / argumento | Descrição | Valor no código |
|---|---|---|---|
| Topo do arquivo | `BASE_URL` | Raiz do fórum | `https://www.scamwarners.com/forum/` |
| Topo do arquivo | `START_URL` | **Subfórum a coletar** — altere para mudar a categoria | `...viewforum.php?f=6` |
| `salvar_formatado()` | `nome_arquivo` | Nome do `.xlsx` de saída | `lojas_falsas_traduzido.xlsx` |
| Bloco `__main__` | `crawler_scamwarners(150)` | Número de registros válidos a coletar | `150` |

Para reproduzir as outras duas planilhas do repositório, altere `START_URL` para o
subfórum correspondente e ajuste `nome_arquivo`.

---

# Dependências

## Linguagem e runtime

| Dependência | Versão |
|---|---|
| Python | 3.10+ (desenvolvido em 3.13) |
| pip | 22+ |

## Bibliotecas Python

| Biblioteca | Versão testada | Finalidade |
|---|---|---|
| `cloudscraper` | 1.2.71 | Requisições HTTP com bypass da proteção Cloudflare (403) |
| `beautifulsoup4` | 4.12.x | Parsing do HTML e aplicação dos seletores CSS |
| `deep-translator` | 1.11.x | Tradução automática inglês → português (backend Google) |
| `pandas` | 2.x | Construção do DataFrame |
| `openpyxl` | 3.1.x | Escrita do `.xlsx` com ajuste de largura de colunas |

## Recursos de terceiros

| Recurso | Acesso | Custo |
|---|---|---|
| **Fórum ScamWarners** | Público, sem autenticação | Gratuito |
| **API de tradução do Google** (via `deep-translator`) | Endpoint público, sem chave de API | Gratuito |

**Nenhuma chave de API ou credencial é necessária.** Não há custo financeiro associado à
execução.

> **Dependência de serviços externos.** Este é o principal risco à reprodutibilidade deste
> repositório: ambos os recursos são serviços de terceiros fora do controle da autora. Ver
> *Preocupações com segurança*, item 4.

---

# Preocupações com segurança

A execução deste artefato **não oferece risco à máquina do avaliador**: o script faz
requisições HTTP e escreve um `.xlsx` local, sem privilégios administrativos e sem executar
código de terceiros. As preocupações são de **ética de coleta** e de **conteúdo**.

## 1. Ética da coleta automatizada

O scraper foi construído para fins **estritamente acadêmicos** e adota medidas explícitas
de cortesia com o servidor de origem:

- **Delay aleatório de 1,5 a 2,5 segundos** entre requisições de tópicos, mais 1 segundo
  entre páginas de listagem
- **Coleta limitada** ao número de registros solicitado, encerrando assim que o alvo é
  atingido
- **Timeout de 15 segundos** por requisição, evitando conexões penduradas
- Acesso apenas a **conteúdo público**, sem autenticação e sem áreas restritas

O ScamWarners é um fórum público mantido por voluntários que documentam golpes com o
propósito explícito de alertar terceiros — finalidade alinhada ao uso acadêmico aqui feito.

> **Recomendação ao avaliador:** para verificar o funcionamento, execute o *teste mínimo*
> desta documentação, que coleta apenas 3 registros. **Não é necessário — nem desejável —
> reexecutar a coleta completa**, já que as saídas estão versionadas no repositório.

## 2. Conteúdo malicioso nos dados coletados

As planilhas contêm **textos reais de golpes**, com links, endereços de e-mail e números de
telefone usados por golpistas.

> **Não acesse os links nem entre em contato com os endereços ou números** presentes nas
> planilhas. Alguns podem permanecer ativos.

## 3. Dados pessoais de terceiros

Os relatos podem conter nomes, e-mails e identificadores de perfis — tanto de golpistas
quanto, eventualmente, de vítimas que reportaram o caso. O material é disponibilizado
**exclusivamente para pesquisa acadêmica** e não deve ser usado para identificar ou
contatar indivíduos.

## 4. Dependência de serviços externos (risco à reprodutibilidade)

A execução depende de dois serviços fora do controle deste trabalho:

| Risco | Efeito | Mitigação |
|---|---|---|
| Mudança na estrutura HTML do fórum | O seletor `blockquote.uncited` deixa de casar e nenhum registro é coletado | As saídas estão versionadas; a reprodução do dataset não depende de reexecutar a coleta |
| Bloqueio pelo Cloudflare | Requisições passam a retornar 403 | `cloudscraper` mitiga, mas não garante indefinidamente |
| Limite de taxa da API de tradução | Traduções falham | O código preserva o texto original em inglês como fallback |
| Remoção de tópicos do fórum | Links de origem quebram | O texto coletado permanece nas planilhas |

Por essa razão, **as planilhas de saída estão versionadas** e são a fonte de verdade para a
reprodução do dataset — a reexecução do scraper é opcional e não é exigida para verificar
nenhuma reivindicação do artigo.

## 5. Qualidade da tradução automática

A tradução é automática e não foi revisada linha a linha. Erros de tradução estão
presentes no dataset e constituem uma limitação reconhecida do trabalho: eles introduzem
ruído nos dados de treinamento do classificador.

---

# Instalação

Tempo total: aproximadamente **3 minutos**.

## Passo 1 — Obter o repositório

```bash
git clone https://github.com/brunanoroes/scraping-scamwarners.git
cd scraping-scamwarners
```

## Passo 2 — Criar o ambiente virtual

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Passo 3 — Instalar as dependências

```bash
pip install cloudscraper pandas openpyxl beautifulsoup4 deep-translator
```

> Tempo esperado: 1–2 minutos. Espaço em disco: ≈ 100 MB.

## Passo 4 — Verificar a instalação

```bash
python -c "import cloudscraper, bs4, pandas, openpyxl; from deep_translator import GoogleTranslator; print('dependencias ok')"
```

Saída esperada:
```
dependencias ok
```

## Passo 5 — Verificar a conectividade

```bash
python -c "
from deep_translator import GoogleTranslator
print(GoogleTranslator(source='en', target='pt').translate('You have won a prize'))
"
```

Saída esperada: uma tradução em português (por exemplo, `Você ganhou um prêmio`). Se este
passo falhar, o serviço de tradução está indisponível ou bloqueado na sua rede.

Ao final deste passo, o ambiente está pronto.

---

# Teste mínimo

O teste mínimo executa uma coleta **reduzida a 3 registros**, demonstrando as quatro etapas
do coletor (paginação, extração, tradução e exportação) sem impor carga ao servidor de
origem.

## Teste A — Coleta reduzida (≈ 1 minuto)

```bash
python - <<'PY'
from scraping import crawler_scamwarners
import pandas as pd

dados = crawler_scamwarners(3)          # apenas 3 registros
print(f"\nRegistros coletados: {len(dados)}")
for i, d in enumerate(dados, 1):
    print(f"\n--- {i} ---")
    print("Link :", d["Link Original"])
    print("Texto:", d["Conteúdo do Golpe (Traduzido)"][:200], "...")

pd.DataFrame(dados).to_excel("teste_minimo.xlsx", index=False)
print("\nArquivo teste_minimo.xlsx gerado.")
PY
```

**Resultado esperado:**

1. O script imprime o progresso (`Progresso: n/3 concluídos`)
2. **Exatamente 3 registros** são coletados — nenhum vazio, confirmando o descarte de
   tópicos sem conteúdo
3. Cada registro traz um link para um tópico real do ScamWarners e um texto **em
   português** (traduzido do inglês)
4. O arquivo `teste_minimo.xlsx` é gerado

> Recursos: < 512 MB de RAM, ≈ 2 MB de banda, ≈ 1 minuto. Sem custo. O arquivo
> `teste_minimo.xlsx` é descartável e não faz parte do dataset.

## Teste B — Verificar as saídas versionadas (≈ 1 minuto, sem rede)

Este teste **não acessa o fórum** e verifica o produto efetivamente usado no trabalho:

```bash
python - <<'PY'
import pandas as pd
for arq in ("scamwarners_romantico.xlsx",
            "lojas_falsas_traduzido.xlsx",
            "financeiro_traduzido.xlsx"):
    df = pd.read_excel(arq)
    print(f"{arq:<35} {len(df):>4} registros | colunas: {list(df.columns)}")
PY
```

**Resultado esperado:** as três planilhas carregam sem erro, cada uma com as colunas
`Link Original` e `Conteúdo do Golpe (Traduzido)` e com registros em português.

## Solução de problemas

| Problema | Causa provável | Solução |
|---|---|---|
| `403 Forbidden` na listagem | Cloudflare bloqueou a requisição | Aguarde alguns minutos e repita; confirme que `cloudscraper` está instalado (e não apenas `requests`) |
| Nenhum registro coletado | Estrutura HTML do fórum mudou | Verifique se o seletor `blockquote.uncited` ainda existe na página; use o Teste B, que não depende do fórum |
| `Erro na tradução` no console | Limite de taxa da API do Google | O texto original em inglês é preservado; aguarde e repita |
| Execução muito lenta | *Delays* de cortesia | Comportamento esperado e intencional — não os remova |
| `ModuleNotFoundError: cloudscraper` | Dependência ausente | Repita o Passo 3 da instalação |
| `PermissionError` ao salvar o `.xlsx` | Arquivo aberto no Excel | Feche a planilha e repita |

---

# Experimentos

Este repositório **não sustenta uma reivindicação quantitativa própria**: ele documenta a
**procedência** de parte dos dados do artefato principal. Sua função na avaliação é tornar
auditável a origem do dataset — requisito de transparência metodológica, já que a
qualidade do classificador depende diretamente de como os dados foram obtidos.

As reivindicações do artigo são reproduzidas em:
**#1** [treinamento-BERTimbau](https://github.com/brunanoroes/treinamento-BERTimbau) ·
**#2** [Treinamento_TF-IDF-SVM](https://github.com/brunanoroes/Treinamento_TF-IDF-SVM) ·
**#3** [evolucao-prompt-RAG](https://github.com/brunanoroes/evolucao-prompt-RAG) ·
**#4** [VeritaPlugin](https://github.com/brunanoroes/VeritaPlugin) ·
**#5 e #6** [ConteudoExtraVeritaPlugin](https://github.com/brunanoroes/ConteudoExtraVeritaPlugin).

## Contribuição para o dataset BrScamsFacebook

Este coletor produziu as fontes **Externo 1**, **Externo 5** e **Externo 7** do
BrScamsFacebook, que reúne 450 instâncias balanceadas (75 por categoria). A consolidação
das seis fontes externas está documentada em
[ConteudoExtraVeritaPlugin](https://github.com/brunanoroes/ConteudoExtraVeritaPlugin),
arquivo `Datasets Externos/Golpes Datasets Externos.xlsx`.

| Planilha deste repositório | Alimenta a categoria |
|---|---|
| `scamwarners_romantico.xlsx` | Golpes Baseados em Relacionamento |
| `lojas_falsas_traduzido.xlsx` | Fraudes em Lojas Virtuais Falsas |
| `financeiro_traduzido.xlsx` | Golpes de Ganho Financeiro Ilusório |

## Reivindicações #1 e #2 — Procedência dos dados do BrScamsFacebook

As reivindicações #1 (F1-macro do BERTimbau) e #2 (comparação com o baseline) só são
interpretáveis se a origem dos dados de treinamento for auditável. Esta subseção descreve
como o revisor verifica a contribuição deste repositório para essa cadeia de procedência.

**Procedimento (≈ 5 minutos, sem custo):**

1. Execute o **Teste B** para confirmar o conteúdo das planilhas
2. Escolha uma linha qualquer e abra a URL da coluna `Link Original` no navegador
3. Confronte o texto do `blockquote` da página com o conteúdo traduzido da planilha

**Resultado esperado:** o texto da planilha corresponde à tradução para o português do
relato publicado no tópico original. **Alguns links podem ter sido removidos do fórum**
desde a coleta — esse é o comportamento esperado para conteúdo de terceiros, e é
justamente por isso que as planilhas estão versionadas.

**Recursos esperados:** navegador e leitor de planilhas. Tempo: ≈ 5 minutos. Custo: zero.

**Sobre o determinismo.** A coleta **não é determinística**: o conteúdo do fórum muda ao
longo do tempo, tópicos são adicionados e removidos, e a tradução automática pode variar
entre chamadas. Reexecutar `scraping.py` produzirá um conjunto diferente de registros. Por
essa razão, a fonte de verdade para a reprodução do dataset são as **planilhas versionadas
neste repositório**, e não uma nova execução do coletor.

---

# LICENSE

Este artefato é distribuído sob a **Licença MIT**. O texto completo está no arquivo
[LICENSE](LICENSE) deste repositório.

```
MIT License

Copyright (c) 2026 Bruna Norões

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions: [...]
```

A licença MIT cobre o **código do coletor** e a organização dos dados. Os relatos coletados
são conteúdo publicado por terceiros no fórum ScamWarners, reproduzidos em tradução para
fins de pesquisa acadêmica, nas condições da seção *Preocupações com segurança* — uso
restrito a pesquisa, vedadas a identificação de indivíduos e a republicação fora do
contexto de avaliação deste artefato.
