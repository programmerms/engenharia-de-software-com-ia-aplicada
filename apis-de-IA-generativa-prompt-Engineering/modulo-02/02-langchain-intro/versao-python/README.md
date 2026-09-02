# LangChain Intro Python

Baseline Python do projeto Módulo 02 — Integração APIs / LLMs, Projeto 02 —
LangChain Intro.

O projeto demonstra um fluxo determinístico com estado, mensagens, nós e
roteamento condicional usando LangGraph. Ele não chama LLM, não exige API key e
não depende de LangSmith.

## Levantar do zero

### Pré-requisitos

- pyenv;
- Python 3.13.12;
- Poetry 2.x.

### Configurar o Python

Na raiz do projeto, selecione a versão usada nesta jornada e confirme o
interpretador ativo:

    pyenv local 3.13.12
    python --version

O segundo comando deve exibir Python 3.13.12. O arquivo .python-version
registra essa escolha para o pyenv.

### Instalar dependências

O Poetry cria/usa o ambiente virtual e instala exatamente as dependências
registradas no lockfile:

    poetry install

Não é necessário criar ou manter um requirements.txt.

### Executar a aplicação

O comando real para iniciar a aplicação FastAPI com Uvicorn é:

    poetry run uvicorn langchain_intro.app:app --reload

O servidor fica disponível em http://127.0.0.1:8000.

### Executar os testes

    poetry run pytest

A suíte não chama LLM, não exige API key e não depende de LangSmith.

## Contrato e uso da API

A API disponibiliza somente POST /chat. Envie JSON com question contendo pelo
menos cinco caracteres:

    curl -X POST http://127.0.0.1:8000/chat \
      -H 'Content-Type: application/json' \
      -d '{"question":"make this UPPER please"}'

Resposta esperada: "MAKE THIS UPPER PLEASE".

Para o caminho lower:

    curl -X POST http://127.0.0.1:8000/chat \
      -H 'Content-Type: application/json' \
      -d '{"question":"MAKE THIS lower PLEASE"}'

Resposta esperada: "make this lower please".

Para o fallback:

    curl -X POST http://127.0.0.1:8000/chat \
      -H 'Content-Type: application/json' \
      -d '{"question":"HEY THERE!"}'

Resposta esperada: "Unknown command. Try 'make this uppercase' or 'convert to lowercase'".

A presença de upper transforma o texto em maiúsculas; na ausência de upper, a
presença de lower transforma o texto em minúsculas; sem nenhum comando, a API
retorna a mensagem de fallback. upper tem precedência quando os dois termos
aparecem.

## LangGraph Dev: visualizar o mesmo grafo

Além da aplicação HTTP, este projeto pode ser aberto no ambiente oficial de
desenvolvimento do LangGraph. As dependências continuam sendo gerenciadas pelo
Poetry:

    poetry install
    poetry run langgraph dev

O comando inicia um servidor local e informa no terminal a URL da API e a URL da
interface oficial de desenvolvimento/visualização. Para encerrar, use `Ctrl+C`.

O arquivo `langgraph.json`, na raiz, informa ao CLI quais dependências locais usar e
qual grafo carregar. Nesta baseline, a entrada é:

    ./src/langchain_intro/graph.py:graph

Isso significa que o CLI carrega o objeto compilado `graph` que já existe no módulo
Python. Não há um segundo grafo para o ambiente de desenvolvimento. Como o fluxo é
determinístico, a execução não exige LLM, provider, API key ou LangSmith.

### FastAPI e LangGraph Dev são modos diferentes

FastAPI é o servidor HTTP da aplicação. Ele expõe `POST /chat`, valida `question` e
chama `graph.invoke()` para devolver somente o resultado textual. Seu comando é:

    poetry run uvicorn langchain_intro.app:app --reload

LangGraph Dev é o ambiente de desenvolvimento do workflow. Ele lê `langgraph.json`,
carrega o mesmo `graph`, permite visualizar nodes e edges e possibilita executar o
grafo pela interface oficial. Um servidor não precisa estar ativo para o outro
funcionar; em desenvolvimento, eles podem ser iniciados em terminais separados.

### O que observar na visualização

O workflow visual corresponde diretamente à definição em `src/langchain_intro/graph.py`:

    START
      ↓
    identify_intent
      ↓
    conditional routing
      ├── uppercase
      ├── lowercase
      └── fallback
      ↓
    append_response
      ↓
    END

Na prática, `identify_intent` escolhe o caminho pela entrada. `uppercase` converte o
texto para maiúsculas, `lowercase` para minúsculas e `fallback` retorna a mensagem
de comando desconhecido. Os três caminhos convergem em `append_response`.

### Conceitos do grafo

- **State**: dados que percorrem uma execução (`messages`, `command` e `output`).
- **Node**: função que lê o estado e devolve uma atualização, como `uppercase`.
- **Edge**: ligação entre etapas do workflow.
- **Conditional Edge**: ligação cujo destino é escolhido por `route_command`.
- **StateGraph**: descrição do workflow com estado, nodes e edges.
- **`compile()`**: transforma a descrição em um grafo executável.
- **`invoke()`**: executa o grafo com um estado inicial efêmero.
- **`langgraph.json`**: configuração que identifica o grafo Python para o CLI.
- **LangGraph CLI**: ferramenta que inicia o servidor local de desenvolvimento.
- **`langgraph dev`**: comando que disponibiliza a visualização e execução local.

Assim, a interface visual não representa uma implementação diferente: ela torna
visíveis os mesmos nodes, edges, estado e roteamento definidos no código Python.

## Fluxo didático

Cada requisição cria um estado efêmero com messages, command e output. O
percurso entre a API e o grafo é:

    HTTP Request
         ↓
      FastAPI
         ↓
    Graph Input
         ↓
    Identify Command
         ↓
    Conditional Routing
       ↙    ↓     ↘
    upper lower fallback
       ↘    ↓     ↙
         Response
            ↓
       HTTP Response

Dentro do grafo, append_response acrescenta a mensagem final antes de END.
LangGraph representa o estado, os nodes, as edges condicionais, a compilação e
o invoke. LangChain fornece as mensagens humana e de resposta. A identificação
e as transformações são lógica Python determinística.

## Diferenças em relação à referência

A referência usa Fastify, Zod e LangChain/LangGraph em TypeScript. Esta versão
usa FastAPI/Pydantic e as APIs atuais de LangGraph/LangChain em Python, mantendo
o mesmo contrato POST /chat, os três caminhos, o estado conceitual e a
precedência de comandos. A estrutura de arquivos e os nomes não são traduzidos
literalmente.
