"""Grafo determinístico da baseline LangChain Intro.

Este módulo deixa visíveis as principais abstrações do LangGraph:

* o estado é o conjunto de dados que percorre o grafo;
* cada node lê o estado e devolve as alterações de sua responsabilidade;
* a conditional edge escolhe o caminho a partir do comando;
* compile transforma a definição em um grafo executável;
* invoke executa esse grafo com um estado inicial efêmero.
"""

from typing import Annotated, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from langchain_intro.messages import ai_message, human_message

Command = Literal["uppercase", "lowercase", "unknown"]
FALLBACK_MESSAGE = "Unknown command. Try 'make this uppercase' or 'convert to lowercase'"


class GraphState(TypedDict, total=False):
    """Dados compartilhados pelos nodes durante uma única execução.

    messages usa o reducer add_messages do LangGraph para acrescentar a
    resposta ao histórico. command registra o roteamento e output é o valor
    textual que será devolvido pela API. Nenhum campo é persistido.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    command: Command
    output: str


def create_initial_state(question: str) -> GraphState:
    """Cria o estado inicial de uma requisição, sem compartilhar memória."""
    return {
        "messages": [human_message(question)],
        "command": "unknown",
        "output": question,
    }


def identify_intent(state: GraphState) -> GraphState:
    """Implementa o primeiro node: classifica por presença textual.

    A normalização é usada apenas para comparar sem distinção de caixa. O texto
    original continua em output; testar upper primeiro materializa a regra de
    precedência upper > lower.
    """
    last_message = state["messages"][-1]
    input_text = str(last_message.content)
    normalized = input_text.lower()

    if "upper" in normalized:
        command: Command = "uppercase"
    elif "lower" in normalized:
        command = "lowercase"
    else:
        command = "unknown"

    return {"command": command, "output": input_text}


def uppercase_node(state: GraphState) -> GraphState:
    """Node de transformação que converte a saída completa para maiúsculas."""
    return {"output": state["output"].upper()}


def lowercase_node(state: GraphState) -> GraphState:
    """Node de transformação que converte a saída completa para minúsculas."""
    return {"output": state["output"].lower()}


def fallback_node(state: GraphState) -> GraphState:
    """Node do caminho unknown que produz a orientação estável."""
    return {"output": FALLBACK_MESSAGE}


def append_response(state: GraphState) -> GraphState:
    """Node final que converte output em mensagem de resposta."""
    return {"messages": [ai_message(state["output"])]}


def route_command(state: GraphState) -> Command:
    """Conditional edge: escolhe o próximo node pelo comando identificado."""
    return state["command"]


def build_graph():
    """Define, conecta e compila o grafo de processamento.

    StateGraph descreve o workflow; as edges ligam os nodes e a edge
    condicional escolhe um dos três caminhos. compile retorna a aplicação
    executável que será reutilizada sem compartilhar o estado das requisições.
    """
    workflow = StateGraph(GraphState)
    workflow.add_node("identify_intent", identify_intent)
    workflow.add_node("uppercase", uppercase_node)
    workflow.add_node("lowercase", lowercase_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("append_response", append_response)

    workflow.add_edge(START, "identify_intent")
    workflow.add_conditional_edges(
        "identify_intent",
        route_command,
        {
            "uppercase": "uppercase",
            "lowercase": "lowercase",
            "unknown": "fallback",
        },
    )
    workflow.add_edge("uppercase", "append_response")
    workflow.add_edge("lowercase", "append_response")
    workflow.add_edge("fallback", "append_response")
    workflow.add_edge("append_response", END)

    return workflow.compile()


graph = build_graph()


def run_graph(question: str) -> GraphState:
    """Invoke o grafo com um estado inicial e devolve o estado final."""
    return graph.invoke(create_initial_state(question))
