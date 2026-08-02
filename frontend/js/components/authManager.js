import { ApiService } from '../services/api.js';

export class AuthManager {
  constructor() {
    this.backdrop = document.getElementById('auth-backdrop');
    this.loginForm = document.getElementById('login-form');
    this.registerForm = document.getElementById('register-form');
    
    this.tabLoginBtn = document.getElementById('tab-btn-login');
    this.tabRegisterBtn = document.getElementById('tab-btn-register');
    this.panelLogin = document.getElementById('panel-login');
    this.panelRegister = document.getElementById('panel-register');

    this.profileMenu = document.getElementById('user-profile-menu');
    this.profileDropdown = document.getElementById('profile-dropdown-menu');
    this.avatarInitials = document.getElementById('user-avatar-initials');
    this.displayName = document.getElementById('user-display-name');
    this.displayEmail = document.getElementById('user-display-email');
    this.btnLogout = document.getElementById('btn-logout');

    this.bindEvents();
    this.checkAuthState();
  }

  bindEvents() {
    // Tab switching
    this.tabLoginBtn?.addEventListener('click', () => this.switchTab('login'));
    this.tabRegisterBtn?.addEventListener('click', () => this.switchTab('register'));

    // Forms
    this.loginForm?.addEventListener('submit', (e) => this.handleLogin(e));
    this.registerForm?.addEventListener('submit', (e) => this.handleRegister(e));

    // Profile menu toggle
    this.profileMenu?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.profileDropdown?.classList.toggle('active');
    });

    // Close dropdown on click outside
    document.addEventListener('click', () => {
      this.profileDropdown?.classList.remove('active');
    });

    // Logout
    this.btnLogout?.addEventListener('click', () => this.logout());

    // Intercept unauthorized requests
    window.addEventListener('auth-unauthorized', () => {
      this.showToast('Authentication required. Please sign in.', 'warning');
      this.showAuthOverlay();
    });

    // Forgot password placeholder
    document.getElementById('auth-forgot-password-placeholder')?.addEventListener('click', () => {
      this.showToast('Reset password link has been sent to your email (Demo only)', 'info');
    });
  }

  switchTab(tab) {
    if (tab === 'login') {
      this.tabLoginBtn?.classList.add('active');
      this.tabRegisterBtn?.classList.remove('active');
      this.panelLogin?.classList.add('active');
      this.panelRegister?.classList.remove('active');
    } else {
      this.tabRegisterBtn?.classList.add('active');
      this.tabLoginBtn?.classList.remove('active');
      this.panelRegister?.classList.add('active');
      this.panelLogin?.classList.remove('active');
    }
  }

  async checkAuthState() {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const res = await ApiService.getMe();
        if (res.success) {
          this.setCurrentUser(res.data);
          this.hideAuthOverlay();
          window.app?.refreshAll();
        } else {
          this.logout();
        }
      } catch (err) {
        console.error('Failed to verify token on startup:', err);
        this.logout();
      }
    } else {
      this.showAuthOverlay();
    }
  }

  async handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
      const res = await ApiService.login(email, password);
      if (res.success && res.data) {
        localStorage.setItem('token', res.data.access_token);
        this.setCurrentUser(res.data.user);
        this.hideAuthOverlay();
        this.showToast('Welcome back!', 'success');
        
        // Refresh all app components
        window.app?.refreshAll();
      }
    } catch (err) {
      this.showToast(err.message || 'Invalid email or password.', 'danger');
    }
  }

  async handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;

    if (password !== confirmPassword) {
      this.showToast('Passwords do not match.', 'danger');
      return;
    }

    if (password.length < 8) {
      this.showToast('Password must be at least 8 characters.', 'danger');
      return;
    }

    try {
      const res = await ApiService.register(fullName, email, password, confirmPassword);
      if (res.success && res.data) {
        localStorage.setItem('token', res.data.access_token);
        this.setCurrentUser(res.data.user);
        this.hideAuthOverlay();
        this.showToast('Registration successful! Welcome!', 'success');
        
        window.app?.refreshAll();
      }
    } catch (err) {
      this.showToast(err.message || 'Registration failed.', 'danger');
    }
  }

  setCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
    
    // Set UI initials
    if (this.avatarInitials) {
      const parts = (user.full_name || '').split(' ');
      const initials = parts.map(p => p[0]).join('').substring(0, 2).toUpperCase();
      this.avatarInitials.innerText = initials || 'U';
    }

    // Set header display info
    if (this.displayName) {
      this.displayName.innerText = user.full_name;
    }
    if (this.displayEmail) {
      this.displayEmail.innerText = user.email;
    }

    // Dynamic greeting banner inside Dashboard tab
    const dashboardTitle = document.querySelector('#tab-dashboard h3');
    if (dashboardTitle) {
      dashboardTitle.innerHTML = `Welcome, ${user.full_name}`;
    }
  }

  showAuthOverlay() {
    this.backdrop?.classList.add('active');
    this.profileMenu?.setAttribute('style', 'display: none !important');
    
    // Clear forms
    if (this.loginForm) this.loginForm.reset();
    if (this.registerForm) this.registerForm.reset();
    this.switchTab('login');
  }

  hideAuthOverlay() {
    this.backdrop?.classList.remove('active');
    this.profileMenu?.removeAttribute('style');
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.showAuthOverlay();
    this.showToast('Logged out successfully.', 'info');
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
}
