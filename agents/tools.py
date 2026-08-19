from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from agents.tools import (
    search_company_knowledge,
    create_complaint,
    get_customer_complaint_status
)


# =========================================================
# LLM
# =========================================================

llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0.2,
)


# =========================================================
# TOOLS
# =========================================================

tools = [

    search_company_knowledge,

    create_complaint,

    get_customer_complaint_status

]


# =========================================================
# AGENT
# =========================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
You are the AppInSnap customer support assistant.

Your job is to help customers with:

1. Company information
2. Services
3. Policies
4. FAQs
5. Customer complaints
6. Complaint status

Rules:

- Use the company knowledge tool for company-related questions.
- Use the complaint tool when the customer wants to register a complaint.
- Use the status tool when the customer wants to check complaints.
- Do not invent company information.
- Do not invent complaint IDs.
- Do not invent complaint statuses.
- Use information returned by tools.
- Give concise and professional answers.
"""
)