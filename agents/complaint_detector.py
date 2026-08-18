import re


COMPLAINT_PATTERNS = [

    # User explicitly wants to complain
    r"\bi want to complain\b",
    r"\bi want to register\b",
    r"\bi want to file\b",
    r"\bregister a complaint\b",
    r"\bfile a complaint\b",
    r"\bmake a complaint\b",
    r"\bi have a complaint\b",
    r"\bcomplain against\b",
    r"\bcomplaint against\b",
    r"\bi want to report\b",

    # Problems
    r"\bnot working\b",
    r"\bdoesn't work\b",
    r"\bdoes not work\b",
    r"\bwon't work\b",
    r"\bfailed\b",
    r"\bfails\b",
    r"\bfailure\b",

    # Technical problems
    r"\bbug\b",
    r"\bcrash\b",
    r"\bcrashing\b",
    r"\berror\b",
    r"\bexception\b",
    r"\bissue\b",
    r"\bproblem\b",

    # Billing
    r"\bcharged twice\b",
    r"\bdouble charged\b",
    r"\bwrong charge\b",
    r"\bpayment failed\b",
    r"\bpayment issue\b",
    r"\brefund\b",

    # Account
    r"\bcannot login\b",
    r"\bcan't login\b",
    r"\bcannot log in\b",
    r"\bcan't log in\b",
    r"\blocked out\b",

    # Service
    r"\bnot receiving\b",
    r"\bnot received\b",
    r"\bmissing\b",
    r"\bdelayed\b",
]


def is_complaint(text):

    if not text:
        return False

    text = text.lower().strip()

    for pattern in COMPLAINT_PATTERNS:

        if re.search(pattern, text):
            return True

    return False