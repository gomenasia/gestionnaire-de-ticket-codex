
(() => {
    const CURRENT_USER_ID = parseInt(document.body.dataset.userId);

    const socket = typeof window.io === "function"
        ? window.io({ transports: ["websocket", "polling"] })
        : null

    function showNotificationToast(message, type) {  //TODO ============= afiche les notification en pop up=============
        const toast = document.createElement("div");
        toast.className = `toast toast--${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function updateNotificationBadge() {             // ============= compte le nombre de notif ============
        const badge = document.querySelector(".notif_badge");
        if (badge) {
            fetch(`/api/notification/unread-counts`)
                .then(res => res.json())
                .then(count => {
                    badge.textContent = count;
                });
            badge.classList.remove("collapsed");
            }; 
        }

    const content_notifications = document.querySelector(".notification");
    const list_notification = document.querySelector(".notifications");

    if (content_notifications) {                          // ============= afiche la div notification =============
        content_notifications.addEventListener("click", () => {
            list_notification.classList.toggle("open")
            const badge = document.querySelector(".notif_badge");
            if (badge) {
                badge.textContent = 0;
                badge.classList.add("collapsed")
            }
            if (list_notification && list_notification.classList.contains("open")) {
                if (CURRENT_USER_ID){
                    update_notif_display(CURRENT_USER_ID);
                }
            }
        });
    }

    function update_notif_display(user_id) {         // ============= acualise la liste de notif =============
        fetch(`/api/notification/${user_id}`)
            .then(res => res.json())
            .then(notifs => {
            notifs.forEach(notif => {
                // Convertir UTC → heure locale du navigateur
                const date = new Date(notif.created_at);
                const local_time = new Intl.DateTimeFormat("fr-FR", {
                    dateStyle: "short",
                    timeStyle: "short",
                    timeZone: "Europe/Paris"
                }).format(date);

                list_notification.innerHTML += `
                <li class="notif-item ${notif.is_read ? '' : 'unread'} data-notification-id="${notif.id}"">
                    <p>${notif.message}</p>
                    <small>${local_time}</small>
                </li>
                `;
            });
        });
        Array.from(list_notification.children).forEach(li_notif => {
            li_notif.addEventListener('click', () => {
                mark_notification_read(li_notif.dataset.notificationId)
            });
        });
    }

    async function mark_notification_read(notif_id) {
        await fetch('/api/notification/mark-read', {
            method:  'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ notification_id: notif_id }),
        });
    }

    addEventListener("DOMContentLoaded", () => {
        if (CURRENT_USER_ID != null){
            updateNotificationBadge();
        }
    });

    if (!socket) {
        // Pas de transport temps réel disponible: on garde le comportement UI (toggle) uniquement
        return
    }

    socket.on("connect", () => {
        console.log("WebSocket connecté");
    });

    // Écouter les nouvelles notifications
    socket.on("new_notification", (notif) => {
        showNotificationToast(notif.message, notif.type);
        updateNotificationBadge();  // incrémenter le compteur dans le menu

        if (CURRENT_USER_ID){
            update_notif_display(CURRENT_USER_ID);
        }
    });
})()