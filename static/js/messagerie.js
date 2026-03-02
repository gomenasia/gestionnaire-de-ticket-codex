(() => {
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
            const panel = document.querySelector(`#discussion-${channelId}`)
            if (!panel) {
                return
            }

            panel.classList.toggle("collapsed")

            const isOpen = !panel.classList.contains("collapsed")
            if (isOpen && socket && !joinedChannels.has(channelId)) {
                socket.emit("join", { channel_id: Number(channelId) })
                joinedChannels.add(channelId)
            }
        })
    })

    if (!socket) {
        // Pas de transport temps réel disponible: on garde le comportement UI (toggle) uniquement.
        return
    }

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
        const panel = document.getElementById(`#discussion-${msg.channel_id}`)
        if (!panel) {
            return
        }

        const p = document.createElement("p")
        p.innerHTML = `<strong>${msg.author}</strong> : ${msg.content}`

        const form = panel.querySelector("form")
        const notice = panel.querySelector(".message.warning")

        if (form) {
            form.before(p)
        } else if (notice) {
            notice.before(p)
        } else {
            panel.appendChild(p)
        }
    })

    socket.on("error_message", (payload) => {
        if (!payload || !payload.message) {
            return
        }
        console.warn(payload.message)
    })
})()