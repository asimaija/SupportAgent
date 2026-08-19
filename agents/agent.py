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
# SYSTEM PROMPT
# =========================================================

system_prompt = """
You are the AppInSnap customer support assistant.

You ONLY support questions related to AppInSnap.

You can help with:

1. AppInSnap company information
2. AppInSnap services
3. AppInSnap policies
4. AppInSnap FAQs
5. Customer complaints
6. Customer complaint status


IMPORTANT RULES:

COMPANY QUESTIONS
-----------------

For questions about AppInSnap, its services,
policies, FAQs, or company information:

ALWAYS use the search_company_knowledge tool.

Do NOT answer company questions from your
pretrained knowledge.

Use ONLY the information returned by
search_company_knowledge.


COMPLAINT REGISTRATION
----------------------

When the customer wants to register a complaint:

ALWAYS use the create_complaint tool.

Do not create a complaint yourself.

Do not invent a complaint ID.

Use the complaint ID returned by the tool.


COMPLAINT STATUS
----------------

When the customer asks about their complaint
or complaint status:

ALWAYS use get_customer_complaint_status.

Do not invent a status.

Use only the information returned by the tool.


CUSTOMER INFORMATION
--------------------

The application provides the authenticated
customer's:

Name
Email
User ID

Use this information when calling complaint tools.

Never ask the customer for information that
is already provided by the application.


UNRELATED QUESTIONS
-------------------

If the question is unrelated to AppInSnap,
do NOT answer using your general knowledge.

Politely respond:

"I can help you with AppInSnap services,
policies, FAQs, and customer complaints.
Please ask an AppInSnap-related question."


GENERAL RULES
-------------

- Never invent company information.
- Never invent complaint IDs.
- Never invent complaint statuses.
- Never invent database information.
- Never pretend a tool was called when it was not.
- Use tool results as the source of truth.
- Keep answers concise and professional.
"""


# =========================================================
# CREATE AGENT
# =========================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)


# =========================================================
# RUN AGENT
# =========================================================

def ask_agent(
    question,
    customer_name="",
    customer_email="",
    customer_user_id=""
):
    """
    Send a customer question to the LangChain agent.

    Customer information comes from the application,
    not from the LLM.
    """

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Authenticated customer:

Name: {customer_name}
Email: {customer_email}
User ID: {customer_user_id}

Customer question:

{question}
"""
                }
            ]
        }
    )


    # =====================================================
    # GET FINAL MESSAGE
    # =====================================================

    messages = response.get(
        "messages",
        []
    )


    if not messages:

        return (
            "Sorry, I could not generate "
            "a response."
        )


    # -----------------------------------------------------
    # FIND LAST AI MESSAGE
    # -----------------------------------------------------

    for message in reversed(messages):

        if getattr(message, "type", None) == "ai":

            content = message.content

            if isinstance(content, str):

                return content

            return str(content)


    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    return str(
        messages[-1].content
    )