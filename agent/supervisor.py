from agent.rag_worker import retrieve, build_rag_prompt
from agent.db_worker import run_db_worker
from agent.tools import TOOL_REGISTRY
from agent.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

def classify_intent(query: str, llm: LLMClient) -> str:
    prompt = f"""You have access to a database with an orders table containing:
order details, customer_id, status, prices, refund_amount, dates.
Can this question be answered from the orders database?
Question: {query}
Reply with ONLY one word: 'database' or 'tool'"""
    response = llm.generate(prompt, max_tokens=10, temperature=0.0)
    intent = response.strip().lower()
    if "database" in intent:
        return "database"
    return "tool"

def run_supervisor(query: str) -> dict:
    llm = LLMClient()
    try:
        rag_result = retrieve(query)
        if rag_result["hit"]:
            prompt = build_rag_prompt(query=query, context=rag_result["context"])
            answer = llm.generate(prompt)
            return {"source": "rag", "answer": answer, "score": rag_result["score"]}

        intent = classify_intent(query, llm)
        if intent == "database":
            answer = run_db_worker(query)
            return {"source": "database", "answer": answer}

        tool_name = "web_search"
        tool_output = TOOL_REGISTRY[tool_name]["fn"](query)
        tool_prompt = f"""Use the following information to answer the question.
If the information is not helpful, say so clearly.
TOOL OUTPUT:
{tool_output}
QUESTION: {query}
ANSWER:"""
        answer = llm.generate(tool_prompt)
        return {"source": "tool", "tool": tool_name, "answer": answer}

    except Exception as e:
        logger.exception("Supervisor failed")
        return {"source": "error", "answer": "Something went wrong.", "error": str(e)}