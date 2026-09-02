# Data Model: LangChain Intro Python

## Pergunta

Representa o corpo recebido pela operação HTTP.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---:|---|
| `question` | texto | sim | mínimo de 5 caracteres |

A pergunta é preservada integralmente como entrada do fluxo. Espaços, pontuação e
acentos não são removidos.

## Mensagem

Representa uma unidade do histórico conceitual da execução.

| Atributo conceitual | Significado |
|---|---|
| papel | humano para a entrada ou IA para a resposta |
| conteúdo | texto da pergunta ou saída final |

As mensagens existem somente durante a requisição. Não há relação com usuário,
sessão ou armazenamento persistente.

## Estado do fluxo

| Campo | Tipo conceitual | Inicialização | Atualizações |
|---|---|---|---|
| `messages` | sequência de mensagens | uma mensagem humana com a pergunta | acrescenta uma mensagem de resposta no nó final |
| `command` | `uppercase` | `lowercase` | `unknown` | ainda não identificado | definido pelo nó de identificação |
| `output` | texto | igual à pergunta | substituído pela transformação ou fallback |

## Transições

1. **Entrada**: valida a Pergunta e cria o Estado.
2. **Identificação**: compara uma versão normalizada apenas para detectar termos.
   Se encontrar `upper`, define `uppercase`; caso contrário, se encontrar `lower`,
   define `lowercase`; caso contrário, define `unknown`. Mantém a pergunta original
   em `output`.
3. **Roteamento**: envia o estado ao caminho correspondente ao comando.
4. **Transformação/fallback**: atualiza `output` sem mutar o texto de entrada.
5. **Resposta**: acrescenta a mensagem final ao histórico e encerra.
6. **Saída HTTP**: expõe somente `output`.

## Invariantes

- A pergunta original não é substituída no histórico.
- `upper` sempre tem precedência sobre `lower`.
- O estado não atravessa requisições.
- O corpo de resposta não expõe `messages` nem `command`.
- A transformação altera somente caixa; espaços, pontuação e acentos permanecem.

