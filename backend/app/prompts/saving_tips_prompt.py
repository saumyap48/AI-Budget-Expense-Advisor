SAVING_TIPS_TEMPLATE = """
USER SPENDING CONTEXT:
- Highest Spending Category: {highest_category} (${highest_category_amount:.2f})
- Daily Average Spending: ${average_daily:.2f}
- Recent Expense Items:
{recent_expenses_text}

USER QUESTION:
{user_question}

Provide 3 to 4 actionable, practical saving recommendations tailored specifically to the highest spending category and recent items listed above. Do not suggest saving on categories where zero dollars have been spent.
"""
