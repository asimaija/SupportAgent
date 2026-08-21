# =========================================================
# agents/complaint_classifier.py
#
# The "Classify Complaint" + "Select Department" steps from the
# architecture diagram. Once agents/complaint_detector.py has already
# decided a message IS a complaint, and the customer has typed out
# the details, this module decides WHAT KIND of complaint it is and
# which team should own it.
#
# Deliberately rule-based (regex keyword matching), same style as
# complaint_detector.py, not another LLM call: classifying a few
# dozen words into one of five buckets doesn't need a model, and
# keeping it rule-based means it's instant and free to run on every
# complaint. If you outgrow these categories later, this is the one
# function (classify_complaint) to swap for an LLM call.
# =========================================================

import re


# Ordered — first matching category wins, so put more specific
# categories (Billing, Account) before the catch-all Technical/Service
# patterns that might otherwise shadow them.
CATEGORY_RULES = [

    (
        "Billing",
        "Billing & Payments",
        [
            r"\bcharged twice\b",
            r"\bdouble charged\b",
            r"\bwrong charge\b",
            r"\bovercharged\b",
            r"\bpayment failed\b",
            r"\bpayment issue\b",
            r"\brefund\b",
            r"\bbilling\b",
            r"\binvoice\b",
            r"\bsubscription\b",
        ],
    ),

    (
        "Account",
        "Account Support",
        [
            r"\bcannot login\b",
            r"\bcan't login\b",
            r"\bcannot log in\b",
            r"\bcan't log in\b",
            r"\blocked out\b",
            r"\bpassword\b",
            r"\baccount\b",
            r"\bverification\b",
            r"\botp\b",
        ],
    ),

    (
        "Technical",
        "Engineering",
        [
            r"\bbug\b",
            r"\bcrash",
            r"\berror\b",
            r"\bexception\b",
            r"\bnot working\b",
            r"\bdoesn't work\b",
            r"\bdoes not work\b",
            r"\bwon't work\b",
            r"\bfroze\b",
            r"\bfreezing\b",
            r"\bslow\b",
        ],
    ),

    (
        "Service",
        "Customer Service",
        [
            r"\bnot receiving\b",
            r"\bnot received\b",
            r"\bmissing\b",
            r"\bdelayed\b",
            r"\blate\b",
            r"\bnever arrived\b",
        ],
    ),

]

DEFAULT_CATEGORY = "General"
DEFAULT_DEPARTMENT = "General Support"


def classify_complaint(text):
    """
    Classify a complaint's free-text description into a
    (category, department) pair.

    Falls back to ("General", "General Support") if nothing matches —
    every complaint still gets routed somewhere, it just isn't a
    specific team.
    """

    if not text:
        return DEFAULT_CATEGORY, DEFAULT_DEPARTMENT

    text = text.lower().strip()

    for category, department, patterns in CATEGORY_RULES:

        for pattern in patterns:

            if re.search(pattern, text):

                return category, department

    return DEFAULT_CATEGORY, DEFAULT_DEPARTMENT