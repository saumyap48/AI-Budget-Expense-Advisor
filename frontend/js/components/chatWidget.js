import { ApiService } from '../services/api.js';

export class ChatWidget {
  constructor() {
    this.messagesContainer = document.getElementById('chat-messages');
    this.inputField = document.getElementById('chat-input');
    this.sendBtn = document.getElementById('chat-send-btn');
    this.chipsContainer = document.getElementById('prompt-chips');

    this.bindEvents();
  }

  bindEvents() {
    this.sendBtn?.addEventListener('click', () => this.handleSend());
    this.inputField?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.handleSend();
    });

    // Prompt Chips Click Handlers
    this.chipsContainer?.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const text = chip.dataset.prompt || chip.textContent;
        if (this.inputField) {
          this.inputField.value = text;
          this.handleSend();
        }
      });
    });
  }

  async handleSend() {
    const question = this.inputField?.value.trim();
    if (!question) return;

    // Render User Message
    this.appendMessage('user', question);
    this.inputField.value = '';

    // Disable send button while waiting
    if (this.sendBtn) { this.sendBtn.disabled = true; this.sendBtn.textContent = '...'; }

    // Render Typing Indicator
    const typingElem = this.appendTypingIndicator();

    try {
      const res = await ApiService.sendChatMessage(question);
      typingElem.remove();

      if (res.success && res.data) {
        this.appendMessage('ai', res.data.answer, res.data.retrieved_documents, res.data.is_fallback);
      } else {
        this.appendMessage('ai', 'Sorry, I encountered an issue processing your request.');
      }
    } catch (err) {
      typingElem.remove();
      this.appendMessage('ai', `Error: ${err.message || 'Could not connect to server.'}`);
    } finally {
      if (this.sendBtn) { this.sendBtn.disabled = false; this.sendBtn.textContent = 'Send 🚀'; }
    }
  }

  appendMessage(sender, text, docs = [], isFallback = false) {
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;

    const avatarSymbol = sender === 'user' ? '👤' : '🤖';
    const formattedText = this.formatMarkdown(text);

    let sourcesHtml = '';
    if (docs && docs.length > 0) {
      // Truncate each document content to 80 chars to keep the UI clean
      const tags = docs.map(d => {
        const snippet = (d.content || '').substring(0, 80) + ((d.content || '').length > 80 ? '...' : '');
        return `<span class="context-tag">📄 ${snippet}</span>`;
      }).join('');
      sourcesHtml = `
        <div class="context-sources">
          <div><strong>Retrieved Context Sources (${docs.length}):</strong></div>
          ${tags}
        </div>
      `;
    }

    row.innerHTML = `
      <div class="chat-avatar">${avatarSymbol}</div>
      <div class="chat-bubble">
        <div>${formattedText}</div>
        ${sourcesHtml}
      </div>
    `;

    this.messagesContainer.appendChild(row);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  appendTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'message-row ai';
    row.innerHTML = `
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble">
        <div class="typing-dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    `;
    this.messagesContainer.appendChild(row);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    return row;
  }

  formatMarkdown(str) {
    let text = String(str || '');
    text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    // Bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Bullet points
    text = text.replace(/^\* (.*?)$/gm, '• $1');
    text = text.replace(/^- (.*?)$/gm, '• $1');
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    return text;
  }
}
