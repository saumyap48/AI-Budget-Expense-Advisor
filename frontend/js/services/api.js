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

    // 60-second timeout to prevent indefinite hanging during cold starts
    const timeoutMs = options.timeout || 60000;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    config.signal = controller.signal;

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);

      // 401 interceptor: fires session-expired logout for authenticated routes.
      // Skip for auth endpoints (login/register) that legitimately return 401 for
      // bad credentials — let the caller handle the error instead.
      if (response.status === 401 && !options.skipAuthRedirect) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.dispatchEvent(new CustomEvent('auth-unauthorized'));
        throw new Error('Session expired. Please log in again.');
      }

      let data;
      const text = await response.text();
      try {
        data = JSON.parse(text);
      } catch (jsonErr) {
        if (!response.ok) {
          const err = new Error(`Server error (${response.status}): ${text.substring(0, 150) || response.statusText}`);
          err.status = response.status;
          throw err;
        }
        throw new Error('Invalid JSON response received from server.');
      }

      if (!response.ok) {
        let errorMsg = '';

        // Priority 1: Check data.detail (FastAPI standard string or validation array)
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (Array.isArray(data.detail)) {
            errorMsg = data.detail.map(d => (typeof d === 'string' ? d : d.msg || d.message || JSON.stringify(d))).join('; ');
          } else if (typeof data.detail === 'object') {
            errorMsg = data.detail.message || data.detail.msg || JSON.stringify(data.detail);
          }
        }

        // Priority 2: Check custom API error format if detail is not plain string
        if (!errorMsg) {
          if (data.error?.details && data.message && data.message !== data.error.details) {
            errorMsg = `${data.message}: ${data.error.details}`;
          } else {
            errorMsg = data.error?.details || data.message;
          }
        }

        if (!errorMsg) {
          errorMsg = `API request failed with status ${response.status}`;
        }

        const err = new Error(errorMsg);
        err.status = response.status;
        err.data = data;
        throw err;
      }

      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. The server may be waking up from cold start, please try again.');
      }
      console.error(`API Error on [${endpoint}]:`, error);
      throw error;
    }
  }

  // Authentication Endpoints
  static login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuthRedirect: true   // 401 = wrong password, not session expiry
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
      }),
      skipAuthRedirect: true
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
