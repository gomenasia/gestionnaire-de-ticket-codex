// Charger socket.io depuis le CDN ou depuis Flask-SocketIO
const socket = io();

socket.on("connect", () => {
    console.log("WebSocket connecté");
});

// Écouter les nouvelles notifications
socket.on("new_notification", (data) => {
    showNotificationToast(data.message, data.type);
    updateNotificationBadge();  // incrémenter le compteur dans le menu

    fetch(`/api/session`)
        .then(response => response.json())
        .then((data) => {
            if(data.success){
                update_notif_display(data.user_id)
            }
        })
    update_notif_display(user_id)
});

function showNotificationToast(message, type) {  // ============= afiche les notification en pop up=============
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function updateNotificationBadge() {             // ============= compte le nombre de notif ============
    const badge = document.querySelector(".notif-badge");
    if (badge) {
        badge.textContent = parseInt(badge.textContent || 0) + 1;
        badge.style.display = "inline";
    }
}


const content_notifications = document.querySelector(".notification");
const list_notification = document.querySelector(".notifications");

if (content_notifications) {                          // ============= afiche les notification =============
    content_notifications.addEventListener("click", () => {
        list_notification.classList.toggle("open")
        if (list_notification) {
            fetch(`/api/session`)
                .then(response => response.json())
                .then((data) => {
                    if(data.success){
                        update_notif_display(data.user_id)
                    }
                })
        }
    });
}

function update_notif_display(user_id) {         // ============= acualise la liste de notif =============
    fetch(`/notification/${user_id}`)
        .then(res => res.json())
        .then(notifs => {
        const container = document.getElementById('notif-container');
        notifs.forEach(notif => {
            container.innerHTML += `
            <li class="notif-item ${notif.is_read ? '' : 'unread'}">
                <p>${notif.message}</p>
                <small>${notif.created_at}</small>
            </li>
            `;
        });
    }); 
}