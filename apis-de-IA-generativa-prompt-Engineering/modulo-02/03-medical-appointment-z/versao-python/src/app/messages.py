"""Mensagens LangChain usadas no histórico efêmero de uma execução.

As mensagens tornam explícito o papel de cada texto no fluxo: a entrada é uma
mensagem humana e o resultado é uma mensagem de resposta. Elas não representam
memória persistente nem exigem um modelo de linguagem.
"""

from langchain_core.messages import AIMessage, HumanMessage


def human_message(question: str) -> HumanMessage:
    """Cria a mensagem humana que inicia uma execução do grafo."""
    return HumanMessage(content=question)


def ai_message(output: str) -> AIMessage:
    """Cria a mensagem de IA que encerra o histórico conceitual."""
    return AIMessage(content=output)
