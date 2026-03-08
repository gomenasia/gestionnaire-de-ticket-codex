// Charger socket.io depuis le CDN ou depuis Flask-SocketIO
const socket = io();

socket.on("connect", () => {
    console.log("WebSocket connecté");
});

// Écouter les nouvelles notifications
socket.on("new_notification", (data) => {
    showNotificationToast(data.message, data.type);
    updateNotificationBadge();  // incrémenter le compteur dans le menu
});

function showNotificationToast(message, type) {
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function updateNotificationBadge() {
    const badge = document.querySelector(".notif-badge");
    if (badge) {
        badge.textContent = parseInt(badge.textContent || 0) + 1;
        badge.style.display = "inline";
    }
}