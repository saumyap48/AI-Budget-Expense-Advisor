import { ApiService } from '../services/api.js';
import { chartManager } from './chartManager.js';

export class AnalyticsView {
  constructor() {
    this.totalSpentEl = document.getElementById('stat-total-spent');
    this.dailyAvgEl = document.getElementById('stat-daily-avg');
    this.topCatEl = document.getElementById('stat-top-cat');
    this.healthScoreEl = document.getElementById('stat-health-score');
    this.topSpendersList = document.getElementById('top-spenders-list');
  }

  async loadAnalytics() {
    try {
      const res = await ApiService.getAnalytics();
      if (res.success && res.data) {
        this.render(res.data);
        chartManager.updateCharts(res.data);
      }
    } catch (err) {
      console.error('Failed to load analytics metrics:', err);
    }
  }

  render(data) {
    if (this.totalSpentEl) this.totalSpentEl.textContent = `$${data.total_expenses.toFixed(2)}`;
    if (this.dailyAvgEl) this.dailyAvgEl.textContent = `$${data.average_daily_spending.toFixed(2)}/day`;

    if (this.topCatEl) {
      if (data.highest_spending_category) {
        this.topCatEl.textContent = `${data.highest_spending_category.category} ($${data.highest_spending_category.total_amount.toFixed(2)})`;
      } else {
        this.topCatEl.textContent = 'None';
      }
    }

    if (this.healthScoreEl) {
      this.healthScoreEl.textContent = `${data.financial_health_score}/100`;
    }

    // Top 5 Largest Expenses List
    if (this.topSpendersList) {
      if (data.top_largest_expenses.length === 0) {
        this.topSpendersList.innerHTML = '<p style="color: var(--text-muted); padding: 12px 0;">No expenses recorded yet.</p>';
      } else {
        this.topSpendersList.innerHTML = data.top_largest_expenses.map(exp => `
          <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color);">
            <div>
              <strong>${this.escapeHtml(exp.description)}</strong>
              <div style="font-size: 0.75rem; color: var(--text-muted);">${exp.category} • ${exp.date}</div>
            </div>
            <div style="font-weight: 700; color: var(--text-primary);">$${parseFloat(exp.amount).toFixed(2)}</div>
          </div>
        `).join('');
      }
    }
  }

  escapeHtml(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}
