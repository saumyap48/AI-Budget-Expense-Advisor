import { AuthManager } from './components/authManager.js';
import { ExpenseManager } from './components/expenseManager.js';
import { BudgetTracker } from './components/budgetTracker.js';
import { AnalyticsView } from './components/analyticsView.js';
import { ChatWidget } from './components/chatWidget.js';

class App {
  constructor() {
    // AuthManager first to block unauthorized requests on start
    this.authManager = new AuthManager();
    
    this.expenseManager = new ExpenseManager();
    this.budgetTracker = new BudgetTracker();
    this.analyticsView = new AnalyticsView();
    this.chatWidget = new ChatWidget();

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

        // Only refresh views if logged in
        const token = localStorage.getItem('token');
        if (token && (targetTab === 'analytics' || targetTab === 'dashboard')) {
          this.analyticsView.loadAnalytics();
        }
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
  window.app = new App();
});
