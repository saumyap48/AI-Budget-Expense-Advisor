import { ApiService } from '../services/api.js';

export class BudgetTracker {
  constructor() {
    this.banner = document.getElementById('budget-status-banner');
    this.fillBar = document.getElementById('budget-progress-fill');
    this.spentEl = document.getElementById('budget-spent-val');
    this.limitEl = document.getElementById('budget-limit-val');
    this.remEl = document.getElementById('budget-remaining-val');
    this.pctEl = document.getElementById('budget-pct-val');
    this.modal = document.getElementById('budget-modal');
    this.form = document.getElementById('budget-form');

    this.bindEvents();
  }

  bindEvents() {
    document.getElementById('btn-set-budget')?.addEventListener('click', () => this.openModal());
    document.getElementById('budget-modal-close')?.addEventListener('click', () => this.closeModal());
    document.getElementById('btn-cancel-budget')?.addEventListener('click', () => this.closeModal());

    this.form?.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  async loadBudget() {
    try {
      const now = new Date();
      const res = await ApiService.getBudget(now.getMonth() + 1, now.getFullYear());

      if (res.success && res.data) {
        this.render(res.data);
      }
    } catch (err) {
      console.error('Failed to load budget status:', err);
    }
  }

  render(data) {
    if (this.spentEl) this.spentEl.textContent = `$${data.total_spent.toFixed(2)}`;
    if (this.limitEl) this.limitEl.textContent = `$${data.monthly_budget.toFixed(2)}`;
    if (this.remEl) this.remEl.textContent = `$${data.remaining_balance.toFixed(2)}`;
    if (this.pctEl) this.pctEl.textContent = `${data.percentage_spent.toFixed(1)}%`;

    // Progress Bar Fill
    const pct = Math.min(100, data.percentage_spent);
    if (this.fillBar) {
      this.fillBar.style.width = `${pct}%`;
      this.fillBar.className = `progress-bar-fill fill-${data.status_level}`;
    }

    // Status Banner - prefix an icon based on status level for visual clarity
    const iconMap = { exceeded: '🚨', warning: '⚠️', normal: '✅', not_set: 'ℹ️' };
    const icon = iconMap[data.status_level] || 'ℹ️';
    if (this.banner) {
      this.banner.className = `budget-status-banner banner-${data.status_level}`;
      this.banner.innerHTML = `<span>${icon} ${data.message}</span>`;
    }

  }

  openModal() {
    const now = new Date();
    document.getElementById('bg-month').value = now.getMonth() + 1;
    document.getElementById('bg-year').value = now.getFullYear();
    this.modal.classList.add('active');
  }

  closeModal() {
    this.modal.classList.remove('active');
  }

  async handleSubmit(e) {
    e.preventDefault();
    const payload = {
      monthly_budget: parseFloat(document.getElementById('bg-amount').value),
      month: parseInt(document.getElementById('bg-month').value, 10),
      year: parseInt(document.getElementById('bg-year').value, 10)
    };

    if (payload.monthly_budget <= 0) {
      alert('Monthly budget must be greater than zero');
      return;
    }

    try {
      const res = await ApiService.setBudget(payload);
      if (res.success) {
        this.render(res.data);
        this.closeModal();
        window.app?.refreshAll();
      }
    } catch (err) {
      alert(err.message || 'Failed to update budget');
    }
  }
}
