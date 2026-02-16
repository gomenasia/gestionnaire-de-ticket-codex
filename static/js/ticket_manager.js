class TicketManager {
    constructor() {
        this.form = document.querySelector('.filters form');
        this.ticketsContainer = document.querySelector('.ticket-list');
        
        // Éléments de filtrage
        this.statusSelect = document.getElementById('status');
        this.sortSelect = document.getElementById('sort');
        this.searchInput = document.getElementById('q');
        this.authorInput = document.getElementById('author');
        this.overdueCheckbox = document.getElementById('overdue');
        
        if (!this.form || !this.ticketsContainer) {
            console.error('Éléments requis introuvables');
            return;
        }
        
        this.initializeEventListeners();
        
        // Charger depuis l'URL au démarrage
        this.loadFromURL();
    }

    initializeEventListeners() {
        // Empêcher la soumission du formulaire
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.loadTickets();
        });
        
        // Écouteurs pour changements instantanés
        this.statusSelect?.addEventListener('change', () => this.loadTickets());
        this.sortSelect?.addEventListener('change', () => this.loadTickets());
        this.overdueCheckbox?.addEventListener('change', () => this.loadTickets());
        
        // Debounce pour les champs de recherche
        let searchTimeout;
        this.searchInput?.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => this.loadTickets(), 300);
        });
        
        let authorTimeout;
        this.authorInput?.addEventListener('input', () => {
            clearTimeout(authorTimeout);
            authorTimeout = setTimeout(() => this.loadTickets(), 300);
        });
    }

    loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        if (params.has('status')) {
            this.statusSelect.value = params.get('status');
        }
        if (params.has('sort')) {
            this.sortSelect.value = params.get('sort');
        }
        if (params.has('q')) {
            this.searchInput.value = params.get('q');
        }
        if (params.has('author')) {
            this.authorInput.value = params.get('author');
        }
        if (params.has('overdue')) {
            this.overdueCheckbox.checked = params.get('overdue') === '1';
        }
    }

    getFilterParams() {
        const params = new URLSearchParams();
        
        if (this.statusSelect?.value && this.statusSelect.value !== 'all') {
            params.append('status', this.statusSelect.value);
        }
        
        if (this.sortSelect?.value) {
            params.append('sort', this.sortSelect.value);
        }
        
        if (this.searchInput?.value.trim()) {
            params.append('q', this.searchInput.value.trim());
        }
        
        if (this.authorInput?.value.trim()) {
            params.append('author', this.authorInput.value.trim());
        }
        
        if (this.overdueCheckbox?.checked) {
            params.append('overdue', '1');
        }
        
        return params;
    }

    async loadTickets() {
        try {
            this.showLoading();
            
            const params = this.getFilterParams();
            const response = await fetch(`/api/tickets?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des tickets');
            }
            
            const data = await response.json();
            this.renderTickets(data.tickets);
            
            // Mettre à jour l'URL sans recharger
            this.updateURL(params);
            
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Impossible de charger les tickets');
        } finally {
            this.hideLoading();
        }
    }

    renderTickets(tickets) {
        if (!this.ticketsContainer) return;
        
        if (tickets.length === 0) {
            this.ticketsContainer.innerHTML = '<p>Aucun ticket ne correspond à vos critères.</p>';
            return;
        }
        
        this.ticketsContainer.innerHTML = tickets.map(ticket => this.createTicketHTML(ticket)).join('');
        
        // Réattacher les événements pour les formulaires admin
        this.attachAdminFormListeners();
    }

    createTicketHTML(ticket) {
        const statusLabel = ticket.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        const createdDate = this.formatDate(ticket.created_at);
        const deadlineInfo = this.getDeadlineHTML(ticket);
        const authorActions = this.getAuthorActionsHTML(ticket);
        const adminResponse = this.getAdminResponseHTML(ticket);
        const adminForm = this.getAdminFormHTML(ticket);
        
        return `
            <article class="ticket" data-ticket-id="${ticket.id}">
                <div class="ticket-head">
                    <h3>${this.escapeHtml(ticket.title)}</h3>
                    <span class="status ${ticket.status}">${statusLabel}</span>
                </div>
                <p>${this.escapeHtml(ticket.content)}</p>
                <small>
                    Auteur: <a href="/user/${ticket.author.id}">${this.escapeHtml(ticket.author.username)}</a> · 
                    Créé le ${createdDate}
                </small>
                
                ${deadlineInfo}
                ${authorActions}
                ${adminResponse}
                ${adminForm}
            </article>
        `;
    }

    getDeadlineHTML(ticket) {
        if (!ticket.deadline) return '';
        
        const now = new Date();
        const deadlineDate = new Date(ticket.deadline);
        const isLate = deadlineDate < now && ticket.status !== 'resolu';
        const countdown = this.formatCountdown(deadlineDate, now);
        const formattedDeadline = this.formatDateShort(ticket.deadline);
        
        return `
            <div class="deadline ${isLate ? 'late' : ''}">
                <strong>Échéance:</strong> ${formattedDeadline} · ${countdown}
            </div>
        `;
    }

    getAuthorActionsHTML(ticket) {
        // Vérifier si l'utilisateur actuel est l'auteur
        // Note: g.user doit être passé depuis le backend ou stocké dans un élément data
        const currentUserId = document.body.dataset.userId; // À ajouter dans votre base.html
        
        if (!currentUserId || parseInt(currentUserId) !== ticket.author.id) {
            return '';
        }
        
        return `
            <div class="author-actions">
                <a class="link-button" href="/ticket/${ticket.id}/edit">Modifier mon ticket</a>
            </div>
        `;
    }

    getAdminResponseHTML(ticket) {
        if (!ticket.admin_response) return '';
        
        return `
            <div class="admin-response">
                <strong>Réponse admin:</strong>
                <p>${this.escapeHtml(ticket.admin_response)}</p>
            </div>
        `;
    }

    getAdminFormHTML(ticket) {
        // Vérifier si l'utilisateur est admin
        const isAdmin = document.body.dataset.isAdmin === 'true'; // À ajouter dans votre base.html
        
        if (!isAdmin) return '';
        
        return `
            <form method="post" action="/ticket/${ticket.id}/admin_update" class="admin-form" data-ticket-id="${ticket.id}">
                <select name="status">
                    <option value="en_attente" ${ticket.status === 'en_attente' ? 'selected' : ''}>En attente</option>
                    <option value="en_cours" ${ticket.status === 'en_cours' ? 'selected' : ''}>En cours</option>
                    <option value="resolu" ${ticket.status === 'resolu' ? 'selected' : ''}>Résolu</option>
                </select>
                <textarea name="admin_response" rows="2" placeholder="Réponse administrateur">${ticket.admin_response || ''}</textarea>
                <button type="submit">Mettre à jour</button>
            </form>
        `;
    }

    attachAdminFormListeners() {
        const adminForms = document.querySelectorAll('.admin-form');
        
        adminForms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const ticketId = form.dataset.ticketId;
                const formData = new FormData(form);
                
                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        // Recharger les tickets après mise à jour
                        this.loadTickets();
                        this.showSuccessMessage('Ticket mis à jour avec succès');
                    } else {
                        throw new Error('Erreur lors de la mise à jour');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    alert('Impossible de mettre à jour le ticket');
                }
            });
        });
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${day}/${month}/${year} ${hours}:${minutes}`;
    }

    formatDateShort(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        
        return `${day}/${month}/${year}`;
    }

    formatCountdown(deadlineDate, now) {
        const diffMs = deadlineDate - now;
        const isPast = diffMs < 0;
        const absDiff = Math.abs(diffMs);
        
        const days = Math.floor(absDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((absDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        
        let text = '';
        if (days > 0) {
            text = `${days} jour${days > 1 ? 's' : ''}`;
            if (hours > 0) {
                text += ` ${hours}h`;
            }
        } else if (hours > 0) {
            text = `${hours} heure${hours > 1 ? 's' : ''}`;
        } else {
            const minutes = Math.floor((absDiff % (1000 * 60 * 60)) / (1000 * 60));
            text = `${minutes} minute${minutes > 1 ? 's' : ''}`;
        }
        
        return isPast ? `En retard de ${text}` : `Dans ${text}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateURL(params) {
        const url = new URL(window.location);
        url.search = params.toString();
        window.history.pushState({}, '', url);
    }

    showLoading() {
        this.ticketsContainer.style.opacity = '0.5';
        this.ticketsContainer.style.pointerEvents = 'none';
    }

    hideLoading() {
        this.ticketsContainer.style.opacity = '1';
        this.ticketsContainer.style.pointerEvents = 'auto';
    }

    showError(message) {
        this.ticketsContainer.innerHTML = `
            <p style="color: #dc3545; padding: 20px; text-align: center;">
                <strong>Erreur:</strong> ${message}
            </p>
        `;
    }

    showSuccessMessage(message) {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Ajouter les animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .ticket-list {
        transition: opacity 0.2s ease;
    }
`;
document.head.appendChild(style);

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    window.ticketManager = new TicketManager();
});
