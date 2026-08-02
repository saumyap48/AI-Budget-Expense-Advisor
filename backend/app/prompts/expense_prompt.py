EXPENSE_QUERY_TEMPLATE = """
RETRIEVED EXPENSE CONTEXT:
{context_documents}

FINANCIAL SUMMARY METRICS:
- Total Spending: ${total_spending:.2f}
- Monthly Budget: ${monthly_budget:.2f}
- Remaining Balance: ${remaining_balance:.2f}
- Highest Category: {highest_category}

USER QUESTION:
{user_question}

Provide a direct, accurate answer to the user's question using ONLY the provided information above.
"""
