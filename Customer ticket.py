import spacy
from spacy.matcher import Matcher
from collections import defaultdict


# ============================================================
# 1. LOAD SPACY NLP MODEL
# ============================================================

print("Loading spaCy model...")

nlp = spacy.load("en_core_web_md")

print("spaCy model loaded successfully!")


# ============================================================
# 2. CATEGORY TRAINING / REFERENCE SENTENCES
# ============================================================

CATEGORY_EXAMPLES = {

    "Billing Team": [
        "My payment failed",
        "My payment was declined",
        "My card payment is not working",
        "I was charged incorrectly",
        "I was charged twice",
        "There is a problem with my transaction",
        "My credit card was charged",
        "My debit card payment failed",
        "I have a payment issue",
        "There is an incorrect charge on my account"
    ],

    "Technical Team": [
        "Unable to login to my account",
        "I cannot login",
        "My password is not working",
        "The application is crashing",
        "The website is not working",
        "The app is not opening",
        "I am getting an error",
        "The website has a technical problem",
        "My account is not accessible",
        "The application stopped working"
    ],

    "Refund Team": [
        "I need a refund",
        "Please refund my order",
        "I want my money back",
        "I want to return my order",
        "How can I get a refund",
        "Please return my money",
        "I want to cancel my order and get a refund",
        "I need to return the product",
        "Can I get my money back",
        "I want a refund for my purchase"
    ],

    "Sales Team": [
        "I want to buy a product",
        "What products do you sell",
        "What is the price of this product",
        "Do you have any offers",
        "Is there a discount available",
        "I want to purchase a product",
        "Tell me about your products",
        "What are the available products",
        "Can you tell me the product price",
        "Are there any promotional offers"
    ]
}


# ============================================================
# 3. PRE-COMPUTE REFERENCE DOCUMENTS
# ============================================================

CATEGORY_DOCS = {}

for category, examples in CATEGORY_EXAMPLES.items():

    CATEGORY_DOCS[category] = [
        nlp(example)
        for example in examples
    ]


# ============================================================
# 4. CREATE SPACY MATCHER
# ============================================================

matcher = Matcher(nlp.vocab)


# ------------------------------------------------------------
# BILLING PATTERNS
# ------------------------------------------------------------

billing_patterns = [

    [
        {"LOWER": {"IN": [
            "payment",
            "transaction",
            "charged",
            "charge",
            "card"
        ]}}
    ],

    [
        {"LOWER": "payment"},
        {"LOWER": {"IN": [
            "failed",
            "declined",
            "rejected",
            "failed."
        ]}}
    ],

    [
        {"LOWER": "charged"},
        {"LOWER": "twice"}
    ]
]


# ------------------------------------------------------------
# TECHNICAL PATTERNS
# ------------------------------------------------------------

technical_patterns = [

    [
        {"LOWER": {"IN": [
            "login",
            "signin",
            "sign-in",
            "password"
        ]}}
    ],

    [
        {"LOWER": {"IN": [
            "error",
            "bug",
            "crash",
            "crashing"
        ]}}
    ],

    [
        {"LOWER": {"IN": [
            "website",
            "application",
            "app"
        ]}},
        {"LOWER": {"IN": [
            "not",
            "isn't",
            "is"
        ]}},
        {"LOWER": {"IN": [
            "working",
            "opening"
        ]}}
    ]
]


# ------------------------------------------------------------
# REFUND PATTERNS
# ------------------------------------------------------------

refund_patterns = [

    [
        {"LOWER": "refund"}
    ],

    [
        {"LOWER": "money"},
        {"LOWER": "back"}
    ],

    [
        {"LOWER": "return"},
        {"LOWER": {"IN": [
            "my",
            "the"
        ]}}
    ]
]


# ------------------------------------------------------------
# SALES PATTERNS
# ------------------------------------------------------------

sales_patterns = [

    [
        {"LOWER": {"IN": [
            "buy",
            "purchase",
            "product"
        ]}}
    ],

    [
        {"LOWER": {"IN": [
            "price",
            "discount",
            "offer",
            "offers",
            "promotion"
        ]}}
    ]
]


# ============================================================
# 5. ADD PATTERNS TO MATCHER
# ============================================================

matcher.add("BILLING", billing_patterns)
matcher.add("TECHNICAL", technical_patterns)
matcher.add("REFUND", refund_patterns)
matcher.add("SALES", sales_patterns)


# ============================================================
# 6. MATCHER FUNCTION
# ============================================================

def get_matcher_results(doc):

    matches = matcher(doc)

    results = defaultdict(list)

    for match_id, start, end in matches:

        category = nlp.vocab.strings[match_id]

        matched_text = doc[start:end].text

        results[category].append(matched_text)

    return dict(results)


# ============================================================
# 7. TEXT SIMILARITY
# ============================================================

def calculate_similarity(doc, category):

    scores = []

    for reference_doc in CATEGORY_DOCS[category]:

        score = doc.similarity(reference_doc)

        scores.append(score)

    if not scores:
        return 0.0

    # Use the strongest matching reference sentence
    return max(scores)


# ============================================================
# 8. CALCULATE ALL CATEGORY SCORES
# ============================================================

def calculate_all_scores(doc):

    similarity_scores = {}

    for category in CATEGORY_EXAMPLES:

        similarity_scores[category] = calculate_similarity(
            doc,
            category
        )

    return similarity_scores


# ============================================================
# 9. ROUTING LOGIC
# ============================================================

def route_ticket(ticket):

    # --------------------------------------------------------
    # NLP PROCESSING
    # --------------------------------------------------------

    doc = nlp(ticket)

    # --------------------------------------------------------
    # TEXT SIMILARITY
    # --------------------------------------------------------

    similarity_scores = calculate_all_scores(doc)

    # --------------------------------------------------------
    # MATCHER
    # --------------------------------------------------------

    matcher_results = get_matcher_results(doc)

    # --------------------------------------------------------
    # COMBINE SCORES
    # --------------------------------------------------------

    final_scores = {}

    for category in CATEGORY_EXAMPLES:

        # Convert category name into matcher name
        matcher_name = category.replace(" Team", "").upper()

        similarity_score = similarity_scores[category]

        # Number of matched patterns
        match_count = len(
            matcher_results.get(matcher_name, [])
        )

        # Matcher bonus
        #
        # We don't want matcher to completely dominate
        # semantic similarity.
        matcher_bonus = min(match_count * 0.05, 0.15)

        final_score = min(
            similarity_score + matcher_bonus,
            1.0
        )

        final_scores[category] = final_score

    # --------------------------------------------------------
    # SELECT BEST CATEGORY
    # --------------------------------------------------------

    best_category = max(
        final_scores,
        key=final_scores.get
    )

    best_score = final_scores[best_category]

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = best_score * 100

    # --------------------------------------------------------
    # ENTITIES
    # --------------------------------------------------------

    entities = []

    for ent in doc.ents:

        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "description": spacy.explain(ent.label_)
        })

    return {
        "ticket": ticket,
        "category": best_category,
        "confidence": confidence,
        "similarity_scores": similarity_scores,
        "final_scores": final_scores,
        "matcher_results": matcher_results,
        "entities": entities
    }


# ============================================================
# 10. DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\n")
    print("=" * 70)
    print("              CUSTOMER SUPPORT TICKET ROUTER")
    print("=" * 70)

    print("\nCustomer Ticket:")
    print(f"  {result['ticket']}")

    # --------------------------------------------------------
    # ENTITIES
    # --------------------------------------------------------

    print("\nNamed Entities:")

    if result["entities"]:

        for entity in result["entities"]:

            print(
                f"  {entity['text']} "
                f"→ {entity['label']} "
                f"({entity['description']})"
            )

    else:
        print("  No named entities detected.")

    # --------------------------------------------------------
    # MATCHER
    # --------------------------------------------------------

    print("\nMatcher Results:")

    if result["matcher_results"]:

        for category, matches in result["matcher_results"].items():

            print(
                f"  {category}: "
                f"{', '.join(matches)}"
            )

    else:

        print("  No predefined patterns detected.")

    # --------------------------------------------------------
    # SIMILARITY
    # --------------------------------------------------------

    print("\nSemantic Similarity:")

    sorted_similarity = sorted(
        result["similarity_scores"].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for category, score in sorted_similarity:

        print(
            f"  {category:<20} "
            f"{score:.4f}"
        )

    # --------------------------------------------------------
    # FINAL SCORES
    # --------------------------------------------------------

    print("\nFinal Scores:")

    sorted_final = sorted(
        result["final_scores"].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for category, score in sorted_final:

        print(
            f"  {category:<20} "
            f"{score:.4f}"
        )

    # --------------------------------------------------------
    # FINAL ROUTING
    # --------------------------------------------------------

    print("\n" + "-" * 70)

    print(
        f"FINAL DEPARTMENT : {result['category']}"
    )

    print(
        f"CONFIDENCE       : {result['confidence']:.2f}%"
    )

    print("-" * 70)


# ============================================================
# 11. TEST CASES
# ============================================================

def run_test_cases():

    test_tickets = [

        # Billing
        "My payment failed while purchasing an item.",

        "I was charged twice for my order.",

        "My credit card payment was declined.",

        # Technical
        "I am unable to login to my account.",

        "The application keeps crashing.",

        "The website is not working.",

        # Refund
        "I need a refund for my order.",

        "I want my money back.",

        "How can I return my product?",

        # Sales
        "What is the price of this product?",

        "Do you have any discounts available?",

        "I want to buy a new product."
    ]

    for ticket in test_tickets:

        result = route_ticket(ticket)

        display_result(result)


# ============================================================
# 12. INTERACTIVE MODE
# ============================================================

def interactive_mode():

    print("\n")
    print("=" * 70)
    print("       CUSTOMER SUPPORT TICKET ROUTING SYSTEM")
    print("=" * 70)

    print("\nDepartments:")
    print("1. Billing Team")
    print("2. Technical Team")
    print("3. Refund Team")
    print("4. Sales Team")

    print("\nType 'exit' to stop.")

    while True:

        ticket = input(
            "\nEnter customer ticket: "
        ).strip()

        if ticket.lower() == "exit":
            print("\nSystem closed.")
            break

        if not ticket:
            print("Please enter a ticket.")
            continue

        result = route_ticket(ticket)

        display_result(result)


# ============================================================
# 13. MAIN
# ============================================================

if __name__ == "__main__":

    # First run predefined examples
    run_test_cases()

    # Then allow user input
    interactive_mode()