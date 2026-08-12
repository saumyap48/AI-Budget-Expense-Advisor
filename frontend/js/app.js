import { AuthManager } from './components/authManager.js';
import { ExpenseManager } from './components/expenseManager.js';
import { BudgetTracker } from './components/budgetTracker.js';
import { AnalyticsView } from './components/analyticsView.js';
import { ChatWidget } from './components/chatWidget.js';

class App {
  constructor() {
    this.expenseManager = new ExpenseManager();
    this.budgetTracker = new BudgetTracker();
    this.analyticsView = new AnalyticsView();
    this.chatWidget = new ChatWidget();

    // AuthManager initialized last so window.app is set before checkAuthState fires refreshAll
    this.authManager = new AuthManager();

    this.initNavigation();
  }

  initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabViews = document.querySelectorAll('.tab-view');

    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const targetTab = item.dataset.tab;

        navItems.forEach(n => n.classList.remove('active'));
        tabViews.forEach(v => v.classList.remove('active'));

        item.classList.add('active');
        document.getElementById(`tab-${targetTab}`)?.classList.add('active');

        // Only refresh data views if user is logged in
        const token = localStorage.getItem('token');
        if (!token) return;

        if (targetTab === 'dashboard') {
          this.analyticsView.loadAnalytics();
          this.budgetTracker.loadBudget();
        } else if (targetTab === 'expenses') {
          this.expenseManager.loadExpenses();
        } else if (targetTab === 'budget') {
          this.budgetTracker.loadBudget();
        }
        // ai-chat tab: no auto-load needed
      });
    });
  }

  async refreshAll() {
    const token = localStorage.getItem('token');
    if (!token) return;

    await Promise.all([
      this.expenseManager.loadExpenses(),
      this.budgetTracker.loadBudget(),
      this.analyticsView.loadAnalytics()
    ]);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Set window.app before AuthManager.checkAuthState fires so refreshAll is available
  window.app = new App();
});
