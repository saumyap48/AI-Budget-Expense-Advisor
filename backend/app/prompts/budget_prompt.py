BUDGET_QUERY_TEMPLATE = """
BUDGET STATUS DATA:
- Monthly Budget: ${monthly_budget:.2f}
- Total Spent This Month: ${total_spent:.2f}
- Remaining Balance: ${remaining_balance:.2f}
- Percentage Used: {percentage_spent:.1f}%
- Status Alert Level: {status_level}

USER QUESTION:
{user_question}

Provide budget guidance and assessment based strictly on the parameters above.
"""
