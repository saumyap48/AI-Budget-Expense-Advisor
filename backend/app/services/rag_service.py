import time
from typing import List
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse, ContextDocument
from app.services.chroma_service import chroma_service
from app.services.gemini_service import gemini_service
from app.services.analytics_service import AnalyticsService
from app.services.budget_service import BudgetService
from app.prompts.system_prompt import SYSTEM_FINANCIAL_ADVISOR_PROMPT
from app.prompts.expense_prompt import EXPENSE_QUERY_TEMPLATE
from app.prompts.saving_tips_prompt import SAVING_TIPS_TEMPLATE
from app.core.logging import ai_logger


class RAGService:

    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        self.budget_service = BudgetService(db)

    def process_chat_query(self, user_id: int, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        query = request.question.strip()

        # 1. Retrieve vector context documents for authenticated user
        retrieved_raw = chroma_service.query_similar_expenses(query=query, user_id=user_id, top_k=5)
        context_docs: List[ContextDocument] = [
            ContextDocument(
                id=doc["id"],
                content=doc["content"],
                category=doc.get("category"),
                amount=doc.get("amount"),
                date=doc.get("date"),
                similarity_score=doc.get("similarity_score")
            )
            for doc in retrieved_raw
        ]

        # 2. Get aggregate financial statistics for user prompt injection
        analytics = self.analytics_service.get_analytics_summary(user_id=user_id)
        budget_status = self.budget_service.get_current_budget_status(user_id=user_id)

        context_str = "\n".join([f"- {doc.content}" for doc in context_docs]) if context_docs else "No specific matching transaction documents found."
        highest_cat_name = analytics.highest_spending_category.category if analytics.highest_spending_category else "None"
        highest_cat_amt = analytics.highest_spending_category.total_amount if analytics.highest_spending_category else 0.0

        # Select prompt template based on query intent
        lower_q = query.lower()
        if "save" in lower_q or "reduce" in lower_q or "cut" in lower_q:
            recent_str = "\n".join([f"- ${e.amount} on {e.description} ({e.category})" for e in analytics.top_recent_expenses])
            user_prompt = SAVING_TIPS_TEMPLATE.format(
                highest_category=highest_cat_name,
                highest_category_amount=highest_cat_amt,
                average_daily=analytics.average_daily_spending,
                recent_expenses_text=recent_str,
                user_question=query
            )
        else:
            user_prompt = EXPENSE_QUERY_TEMPLATE.format(
                context_documents=context_str,
                total_spending=analytics.total_expenses,
                monthly_budget=budget_status.monthly_budget,
                remaining_balance=budget_status.remaining_balance,
                highest_category=highest_cat_name,
                user_question=query
            )

        # 3. Query Gemini API
        answer, is_fallback, processing_time = gemini_service.generate_response(
            system_prompt=SYSTEM_FINANCIAL_ADVISOR_PROMPT,
            user_prompt=user_prompt
        )

        total_time_ms = round((time.time() - start_time) * 1000, 2)
        ai_logger.info(f"Processed RAG chat query for user {user_id} in {total_time_ms}ms (Fallback={is_fallback})")

        return ChatResponse(
            question=query,
            answer=answer,
            retrieved_documents=context_docs,
            model_used=gemini_service.model,
            is_fallback=is_fallback,
            processing_time_ms=total_time_ms
        )
