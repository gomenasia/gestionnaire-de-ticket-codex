(() => {
    const CURRENT_USER_ID   = parseInt(document.body.dataset.userId);
    const ticketList = document.querySelector(".ticket-list")
    if (!ticketList) {
        return
    }

    const socket = typeof window.io === "function"
        ? window.io({ transports: ["websocket", "polling"] })
        : null

    const joinedChannels = new Set()

    // Ouvrir/fermer les discussions (doit fonctionner même sans Socket.IO)
    document.querySelectorAll(".btn-repondre").forEach((btn) => {
        btn.addEventListener("click", () => {
            const channelId = btn.dataset.channelId
            const ticketlId = btn.dataset.ticketId
            const panel = document.querySelector(`#discussion-${channelId}`)
            if (!panel) {
                return
            }

            panel.classList.toggle("collapsed")

            const isOpen = !panel.classList.contains("collapsed")
            if (isOpen && socket && !joinedChannels.has(channelId)) {
                socket.emit("join", { channel_id: Number(channelId) })
                joinedChannels.add(channelId)

                openTicketChat(ticketlId)

                const messagerie = document.getElementById(`message_display-${channelId}`)
                messagerie.scrollTop = messagerie.scrollHeight;

                const input_message = panel.querySelector("form input")
                input_message.focus()
            }
        })
    })

   // =============================================== UNREAD =============================================

    const unreadCounts      = {};   // { "chanelId": count }
    let   pollingInterval   = null;

    // ── Init ──────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        loadUnreadCounts();
        startPolling();
    });

    // ── Polling toutes les 10 secondes ────────────────────────
    function startPolling() {
        pollingInterval = setInterval(async () => {
            await loadUnreadCounts();
        }, 10_000); // 10s — ajuste selon tes besoins
    }

    function stopPolling() {
        clearInterval(pollingInterval);
    }

    // ── Fetch les compteurs depuis l'API ──────────────────────
    async function loadUnreadCounts() {
        try {
            const res  = await fetch('/api/messages/unread-counts');
            if (!res.ok) return;
            const data = await res.json();  // {(channel_id, count)} { 12: 3, 7: 1 }

            Object.entries(data).forEach(([ticketId, count]) => {
                unreadCounts[ticketId] = count;
                updateBadge(ticketId);
            });

            // Remettre à 0 les tickets qui n'apparaissent plus dans la réponse
            Object.keys(unreadCounts).forEach(ticketId => {
                if (!(ticketId in data)) {
                    unreadCounts[ticketId] = 0;
                    updateBadge(ticketId);
                }
            });

        } catch (e) {
            console.warn('Polling non-lus échoué :', e);
        }
    }

    // ── Ouvrir un ticket ──────────────────────────────────────
    async function openTicketChat(ticketId) {
        // Reset badge immédiatement
        unreadCounts[String(ticketId)] = 0;
        updateBadge(String(ticketId));

        // Marquer comme lu côté serveur
        await fetch('/api/messages/mark-read', {
            method:  'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ticket_id: ticketId }),
        });
    }

    // ── Badge UI ──────────────────────────────────────────────
    function updateBadge(ticketId) {
        const item = document.querySelector(`article.ticket[id="${ticketId}"]`);
        if (!item) return;

        let badge = item.querySelector('.unread-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'unread-badge';
            item.appendChild(badge);
        } else{
            alert("badge non reconue") //TODO remove debug
        }

        const count = unreadCounts[ticketId] || 0;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.add('show');
            item.classList.add('has-unread');
        } else {
            badge.classList.remove('show');
            item.classList.remove('has-unread');
        }
    }

    // ── Pause polling si onglet caché (économie réseau) ───────
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopPolling();
        } else {
            loadUnreadCounts();  // refresh immédiat au retour
            startPolling();
        }
    });

    // =================================================== SOCKETIO ===========================================

    if (!socket) {
        // Pas de transport temps réel disponible: on garde le comportement UI (toggle) uniquement.
        return
    }

    //TODO implement typing...

    // Envoi d'un message (uniquement formulaires présents = utilisateurs connectés)
    document.querySelectorAll(".form-message").forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault()

            const channelId = form.dataset.channelId
            const input = form.querySelector("input[name='content']")
            if (!channelId || !input) {
                return
            }

            const content = input.value.trim()
            if (!content) {
                return
            }

            socket.emit("send_message", {
                content,
                channel_id: Number(channelId)
            })
            input.value = ""

        })
    })

    socket.on("new_message", (msg) => {
        const panel = document.getElementById(`message_display-${msg.channel_id}`)
        if (!panel) {
            return
        }
        const user_id = Number(panel.dataset.userId);

        const p = document.createElement("p")
        p.classList.add('conv_message')
        if(msg.author_id === user_id){
            p.classList.add('owned')
            p.innerHTML = msg.content
        } else {
            p.innerHTML = `<strong>${msg.author}</strong> : ${msg.content}`
        }

        const notice = panel.querySelector(".message.warning")

        if (notice) {
            notice.before(p)
        } else {
            panel.appendChild(p)
        }

        panel.scrollTop = panel.scrollHeight; // permet de scroll en bas auto
    })

    socket.on("error_message", (payload) => {
        if (!payload || !payload.message) {
            return
        }
        console.warn(payload.message)
    })
    
    //garder les channel ouvert
    document.querySelectorAll(".btn-repondre").forEach(btn => {
        const channelId = btn.dataset.channelId
        const panel = document.querySelector(`#discussion-${channelId}`)

        // Restaure
        if (localStorage.getItem(`channel-${channelId}`) === 'true') {
            panel.classList.toggle("collapsed");
            
            if (socket && !joinedChannels.has(channelId)) {
                socket.emit("join", { channel_id: Number(channelId) })
                joinedChannels.add(channelId)
            }
        }

        // Sauvegarde
        btn.addEventListener("click", () => {
            localStorage.setItem(`channel-${channelId}`, !panel.classList.contains("collapsed"));
        });
    });
})()
