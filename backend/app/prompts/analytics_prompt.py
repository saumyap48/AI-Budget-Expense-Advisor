ANALYTICS_QUERY_TEMPLATE = """
FINANCIAL ANALYTICS DATA:
- Total Expenses: ${total_expenses:.2f} across {total_count} transactions
- Daily Average Spending: ${average_daily:.2f} / day
- Highest Spending Category: {highest_category} (${highest_category_amount:.2f})
- Lowest Spending Category: {lowest_category} (${lowest_category_amount:.2f})

CATEGORY BREAKDOWN:
{category_breakdown_text}

USER QUESTION:
{user_question}

Provide an analytical breakdown answering the user's question using ONLY the provided data.
"""
