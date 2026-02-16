// ticket_manager_advanced.js - Fonctionnalités avancées optionnelles

// ========================================
// 1. SAUVEGARDE DES FILTRES DANS LOCALSTORAGE
// ========================================

class TicketManagerWithMemory extends TicketManager {
    constructor() {
        super();
        this.loadSavedFilters();
    }

    loadSavedFilters() {
        const saved = localStorage.getItem('ticketFilters');
        if (saved) {
            try {
                const filters = JSON.parse(saved);
                if (this.statusFilter) this.statusFilter.value = filters.status || 'all';
                if (this.sortFilter) this.sortFilter.value = filters.sort || 'recent';
                if (this.searchInput) this.searchInput.value = filters.q || '';
                if (this.authorInput) this.authorInput.value = filters.author || '';
                if (this.overdueCheckbox) this.overdueCheckbox.checked = filters.overdue || false;
            } catch (e) {
                console.error('Erreur lors du chargement des filtres', e);
            }
        }
    }

    saveFilters() {
        const filters = {
            status: this.statusFilter?.value || 'all',
            sort: this.sortFilter?.value || 'recent',
            q: this.searchInput?.value || '',
            author: this.authorInput?.value || '',
            overdue: this.overdueCheckbox?.checked || false
        };
        localStorage.setItem('ticketFilters', JSON.stringify(filters));
    }

    async loadTickets() {
        await super.loadTickets();
        this.saveFilters();
    }
}


// ========================================
// 2. PAGINATION
// ========================================

class TicketManagerWithPagination extends TicketManager {
    constructor() {
        super();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalPages = 1;
        this.paginationContainer = document.getElementById('pagination');
    }

    async loadTickets() {
        try {
            this.showLoading();
            
            const params = this.getFilterParams();
            params.append('page', this.currentPage);
            params.append('per_page', this.itemsPerPage);
            
            const response = await fetch(`/api/tickets?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des tickets');
            }
            
            const data = await response.json();
            this.totalPages = Math.ceil(data.total / this.itemsPerPage);
            
            this.renderTickets(data.tickets);
            this.renderPagination();
            this.updateTicketCount(data.total);
            this.updateURL(params);
            
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Impossible de charger les tickets');
        } finally {
            this.hideLoading();
        }
    }

    renderPagination() {
        if (!this.paginationContainer || this.totalPages <= 1) {
            if (this.paginationContainer) {
                this.paginationContainer.innerHTML = '';
            }
            return;
        }

        let html = '<div class="pagination">';
        
        // Bouton précédent
        if (this.currentPage > 1) {
            html += `<button class="page-btn" data-page="${this.currentPage - 1}">
                <i class="fas fa-chevron-left"></i> Précédent
            </button>`;
        }

        // Numéros de page
        const maxButtons = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(this.totalPages, startPage + maxButtons - 1);

        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }

        if (startPage > 1) {
            html += `<button class="page-btn" data-page="1">1</button>`;
            if (startPage > 2) {
                html += '<span class="page-ellipsis">...</span>';
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const active = i === this.currentPage ? 'active' : '';
            html += `<button class="page-btn ${active}" data-page="${i}">${i}</button>`;
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                html += '<span class="page-ellipsis">...</span>';
            }
            html += `<button class="page-btn" data-page="${this.totalPages}">${this.totalPages}</button>`;
        }

        // Bouton suivant
        if (this.currentPage < this.totalPages) {
            html += `<button class="page-btn" data-page="${this.currentPage + 1}">
                Suivant <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        html += '</div>';
        this.paginationContainer.innerHTML = html;

        // Attacher les événements
        this.paginationContainer.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentPage = parseInt(btn.dataset.page);
                this.loadTickets();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }
}


// ========================================
// 3. EXPORT DES RÉSULTATS
// ========================================

function addExportButton() {
    const exportBtn = document.createElement('button');
    exportBtn.id = 'export-btn';
    exportBtn.className = 'btn btn-secondary';
    exportBtn.innerHTML = '<i class="fas fa-download"></i> Exporter';
    
    const header = document.querySelector('.tickets-header');
    if (header) {
        header.appendChild(exportBtn);
    }

    exportBtn.addEventListener('click', async () => {
        try {
            const params = ticketManager.getFilterParams();
            const response = await fetch(`/api/tickets?${params.toString()}`);
            const data = await response.json();
            
            // Créer CSV
            let csv = 'ID,Titre,Statut,Priorité,Auteur,Date de création,Échéance\n';
            
            data.tickets.forEach(ticket => {
                csv += `${ticket.id},"${ticket.title.replace(/"/g, '""')}",${ticket.status},${ticket.priority},${ticket.author.username},${ticket.created_at},${ticket.deadline || 'N/A'}\n`;
            });
            
            // Télécharger
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `tickets_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();
            
        } catch (error) {
            console.error('Erreur lors de l\'export:', error);
            alert('Erreur lors de l\'export des tickets');
        }
    });
}


// ========================================
// 4. NOTIFICATIONS EN TEMPS RÉEL (avec WebSocket)
// ========================================

class TicketManagerWithRealtime extends TicketManager {
    constructor() {
        super();
        this.initWebSocket();
    }

    initWebSocket() {
        // Adapter selon votre configuration
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/tickets`);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'ticket_update') {
                this.showNotification('Un ticket a été mis à jour');
                this.loadTickets();
            } else if (data.type === 'new_ticket') {
                this.showNotification('Nouveau ticket créé');
                this.loadTickets();
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket fermé, tentative de reconnexion...');
            setTimeout(() => this.initWebSocket(), 5000);
        };
    }

    showNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Tickets', { body: message });
        } else {
            // Toast notification alternative
            const toast = document.createElement('div');
            toast.className = 'toast-notification';
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => toast.classList.add('show'), 100);
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
    }
}


// ========================================
// 5. MODE SOMBRE
// ========================================

class ThemeToggle {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.applyTheme();
        this.createToggleButton();
    }

    createToggleButton() {
        const btn = document.createElement('button');
        btn.id = 'theme-toggle';
        btn.className = 'theme-toggle-btn';
        btn.innerHTML = this.theme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
        
        document.body.appendChild(btn);
        
        btn.addEventListener('click', () => this.toggle());
    }

    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('theme', this.theme);
        
        const btn = document.getElementById('theme-toggle');
        btn.innerHTML = this.theme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }
}


// ========================================
// 6. DRAG & DROP POUR CHANGER LE STATUT
// ========================================

class TicketManagerWithDragDrop extends TicketManager {
    renderTickets(tickets) {
        super.renderTickets(tickets);
        this.initDragAndDrop();
    }

    initDragAndDrop() {
        const cards = document.querySelectorAll('.ticket-card');
        
        cards.forEach(card => {
            card.draggable = true;
            
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('ticketId', card.dataset.ticketId);
                card.classList.add('dragging');
            });
            
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });
        });

        // Zones de dépôt (à créer dans le HTML)
        const dropZones = document.querySelectorAll('.status-drop-zone');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });
            
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });
            
            zone.addEventListener('drop', async (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                
                const ticketId = e.dataTransfer.getData('ticketId');
                const newStatus = zone.dataset.status;
                
                await this.updateTicketStatus(ticketId, newStatus);
            });
        });
    }

    async updateTicketStatus(ticketId, newStatus) {
        try {
            const response = await fetch(`/api/tickets/${ticketId}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            
            if (response.ok) {
                this.loadTickets();
                this.showNotification('Statut mis à jour avec succès');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Impossible de mettre à jour le statut');
        }
    }
}


// ========================================
// 7. FILTRES AVANCÉS MULTIPLES
// ========================================

class AdvancedFilters {
    constructor(ticketManager) {
        this.manager = ticketManager;
        this.activeFilters = [];
        this.createFilterUI();
    }

    createFilterUI() {
        const container = document.createElement('div');
        container.id = 'advanced-filters';
        container.innerHTML = `
            <button id="add-filter-btn" class="btn btn-secondary">
                <i class="fas fa-plus"></i> Ajouter un filtre
            </button>
            <div id="active-filters"></div>
        `;
        
        const filtersContainer = document.querySelector('.filters-container');
        if (filtersContainer) {
            filtersContainer.appendChild(container);
        }

        document.getElementById('add-filter-btn')?.addEventListener('click', () => {
            this.showFilterModal();
        });
    }

    showFilterModal() {
        // Créer une modale pour sélectionner le type de filtre
        const modal = document.createElement('div');
        modal.className = 'filter-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Ajouter un filtre</h3>
                <select id="filter-type">
                    <option value="priority">Priorité</option>
                    <option value="date_range">Plage de dates</option>
                    <option value="tags">Tags</option>
                    <option value="assigned">Assigné à</option>
                </select>
                <button class="btn btn-primary">Ajouter</button>
                <button class="btn btn-secondary">Annuler</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        // Logique de modale...
    }
}


// ========================================
// CSS SUPPLÉMENTAIRE POUR LES FONCTIONNALITÉS
// ========================================

const advancedStyles = `
/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin-top: 30px;
    padding: 20px 0;
}

.page-btn {
    padding: 8px 12px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.page-btn:hover {
    background: #f8f9fa;
    border-color: #007bff;
}

.page-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.page-ellipsis {
    padding: 8px 4px;
    color: #666;
}

/* Toast notifications */
.toast-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #333;
    color: white;
    padding: 15px 20px;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s;
    z-index: 9999;
}

.toast-notification.show {
    transform: translateY(0);
    opacity: 1;
}

/* Theme toggle */
.theme-toggle-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: none;
    background: #007bff;
    color: white;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: all 0.3s;
    z-index: 1000;
}

.theme-toggle-btn:hover {
    transform: scale(1.1);
}

/* Dark theme */
[data-theme="dark"] {
    background: #1a1a1a;
    color: #e0e0e0;
}

[data-theme="dark"] .ticket-card {
    background: #2d2d2d;
    border-color: #404040;
}

[data-theme="dark"] .filters-container {
    background: #2d2d2d;
}

[data-theme="dark"] input,
[data-theme="dark"] select {
    background: #3d3d3d;
    border-color: #505050;
    color: #e0e0e0;
}

/* Drag and drop */
.ticket-card.dragging {
    opacity: 0.5;
    transform: rotate(5deg);
}

.status-drop-zone {
    min-height: 100px;
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 20px;
    margin: 10px;
    transition: all 0.3s;
}

.status-drop-zone.drag-over {
    border-color: #007bff;
    background: rgba(0, 123, 255, 0.1);
}
`;

// Injecter les styles
const styleSheet = document.createElement('style');
styleSheet.textContent = advancedStyles;
document.head.appendChild(styleSheet);