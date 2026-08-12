import { ApiService } from '../services/api.js';
import { store } from '../services/store.js';

export class ExpenseManager {
  constructor() {
    this.tableBody = document.getElementById('expense-table-body');
    this.modal = document.getElementById('expense-modal');
    this.form = document.getElementById('expense-form');
    this.editingId = null;

    this.bindEvents();
  }

  bindEvents() {
    // Add Expense Button
    document.getElementById('btn-add-expense')?.addEventListener('click', () => this.openModal());
    document.getElementById('modal-close-btn')?.addEventListener('click', () => this.closeModal());
    document.getElementById('btn-cancel-modal')?.addEventListener('click', () => this.closeModal());

    // Form Submit
    this.form?.addEventListener('submit', (e) => this.handleSubmit(e));

    // Filters - use debounce for search input to avoid rapid API calls
    document.getElementById('filter-category')?.addEventListener('change', () => this.loadExpenses());
    document.getElementById('search-input')?.addEventListener('input', () => {
      clearTimeout(this._searchTimer);
      this._searchTimer = setTimeout(() => this.loadExpenses(), 400);
    });
  }

  async loadExpenses() {
    try {
      const category = document.getElementById('filter-category')?.value || '';
      const search = document.getElementById('search-input')?.value || '';

      const params = {};
      if (category) params.category = category;
      if (search) params.q = search;

      const res = await ApiService.getExpenses(params);
      if (res.success) {
        store.setState({ expenses: res.data });
        this.renderTable(res.data);
      }
    } catch (err) {
      this.showToast(err.message || 'Failed to load expenses', 'danger');
    }
  }

  renderTable(expenses = []) {
    if (!this.tableBody) return;

    if (expenses.length === 0) {
      this.tableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 32px; color: var(--text-muted);">
            No expenses found. Click <strong>+ Add Expense</strong> to record a new transaction.
          </td>
        </tr>
      `;
      return;
    }

    this.tableBody.innerHTML = expenses.map(exp => `
      <tr>
        <td><strong>${exp.date}</strong></td>
        <td><span class="category-badge">${exp.category}</span></td>
        <td>${this.escapeHtml(exp.description)}</td>
        <td>${exp.payment_method || 'Cash'}</td>
        <td style="font-weight: 700; color: var(--text-primary);">$${parseFloat(exp.amount).toFixed(2)}</td>
        <td class="actions-cell">
          <button class="btn-icon edit" data-id="${exp.id}">✏️</button>
          <button class="btn-icon delete" data-id="${exp.id}">🗑️</button>
        </td>
      </tr>
    `).join('');

    // Attach click listeners to edit/delete buttons
    this.tableBody.querySelectorAll('.btn-icon.edit').forEach(btn => {
      btn.addEventListener('click', () => this.editExpense(btn.dataset.id));
    });

    this.tableBody.querySelectorAll('.btn-icon.delete').forEach(btn => {
      btn.addEventListener('click', () => this.deleteExpense(btn.dataset.id));
    });
  }

  openModal(expense = null) {
    this.editingId = expense ? expense.id : null;
    document.getElementById('modal-title').textContent = expense ? 'Edit Expense' : 'Add Expense';

    if (expense) {
      document.getElementById('exp-amount').value = expense.amount;
      document.getElementById('exp-category').value = expense.category;
      document.getElementById('exp-description').value = expense.description;
      document.getElementById('exp-date').value = expense.date;
      document.getElementById('exp-payment').value = expense.payment_method || 'Cash';
      document.getElementById('exp-notes').value = expense.notes || '';
    } else {
      this.form.reset();
      document.getElementById('exp-date').value = new Date().toISOString().split('T')[0];
    }

    this.modal.classList.add('active');
  }

  closeModal() {
    this.modal.classList.remove('active');
    this.editingId = null;
  }

  async handleSubmit(e) {
    e.preventDefault();

    const payload = {
      amount: parseFloat(document.getElementById('exp-amount').value),
      category: document.getElementById('exp-category').value,
      description: document.getElementById('exp-description').value.trim(),
      date: document.getElementById('exp-date').value,
      payment_method: document.getElementById('exp-payment').value,
      notes: document.getElementById('exp-notes').value.trim() || null
    };

    if (payload.amount <= 0 || isNaN(payload.amount)) {
      this.showToast('Amount must be greater than zero', 'warning');
      return;
    }

    if (!payload.description) {
      this.showToast('Description is required', 'warning');
      return;
    }

    const submitBtn = e.target.querySelector('button[type="submit"]');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Saving...'; }

    try {
      if (this.editingId) {
        await ApiService.updateExpense(this.editingId, payload);
        this.showToast('Expense updated & vector index synced!', 'success');
      } else {
        await ApiService.createExpense(payload);
        this.showToast('Expense added & vector index synced!', 'success');
      }

      this.closeModal();
      window.app?.refreshAll();
    } catch (err) {
      this.showToast(err.message || 'Operation failed', 'danger');
    } finally {
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '💾 Save Expense'; }
    }
  }

  async editExpense(id) {
    try {
      const res = await ApiService.getExpenseById(id);
      if (res.success) {
        this.openModal(res.data);
      }
    } catch (err) {
      this.showToast('Failed to fetch expense details', 'danger');
    }
  }

  async deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) return;

    try {
      await ApiService.deleteExpense(id);
      this.showToast('Expense deleted & purged from vector store', 'success');
      window.app?.refreshAll();
    } catch (err) {
      this.showToast('Failed to delete expense', 'danger');
    }
  }

  showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${msg}</span>`;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 4000);
  }

  escapeHtml(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}
