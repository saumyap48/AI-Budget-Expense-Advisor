import { CONFIG } from '../config.js';

export class ApiService {
  static async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    
    const token = localStorage.getItem('token');
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.dispatchEvent(new CustomEvent('auth-unauthorized'));
        throw new Error('Session expired. Please log in again.');
      }

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.message || data.error?.details || 'API request failed';
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error(`API Error on [${endpoint}]:`, error);
      throw error;
    }
  }

  // Authentication Endpoints
  static login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  static register(fullName, email, password, confirmPassword) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        full_name: fullName,
        email,
        password,
        confirm_password: confirmPassword
      })
    });
  }

  static getMe() {
    return this.request('/auth/me');
  }

  // Expense Endpoints
  static getExpenses(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/expenses?${queryString}`);
  }

  static getExpenseById(id) {
    return this.request(`/expenses/${id}`);
  }

  static createExpense(data) {
    return this.request('/expenses', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static updateExpense(id, data) {
    return this.request(`/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  static deleteExpense(id) {
    return this.request(`/expenses/${id}`, {
      method: 'DELETE'
    });
  }

  // Budget Endpoints
  static getBudget(month, year) {
    let query = '';
    if (month && year) query = `?month=${month}&year=${year}`;
    return this.request(`/budgets/current${query}`);
  }

  static setBudget(data) {
    return this.request('/budgets', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Analytics Endpoint
  static getAnalytics() {
    return this.request('/analytics');
  }

  // AI Chat Endpoint
  static sendChatMessage(question) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({ question })
    });
  }

  // Health Endpoint
  static getHealth() {
    return this.request('/health');
  }
}
