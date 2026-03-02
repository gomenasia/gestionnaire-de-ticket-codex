(() => {
    const socket = io()

    // Ouvrir/fermer les discussions
    document.querySelectorAll(".btn-repondre").forEach(btn => {
        btn.addEventListener("click", () => {
            const channelId = btn.dataset.channelId
            const panel = document.querySelector(`#discussion-${channelId}`)
            panel.classList.toggle("collapsed")

            if (!panel.classList.contains("collapsed")) {
                socket.emit("join", { channel_id: channelId })
            }
        })
    })

    // Envoi d'un message
    document.querySelectorAll(".form-message").forEach(form => {
        form.addEventListener("submit", (e) => {
            e.preventDefault()
            const channelId = form.dataset.channelId
            const input = form.querySelector("input[name='content']")

            socket.emit("send_message", {
                content:    input.value,
                channel_id: channelId
            })
            input.value = ""
        })
    })

    // Réception d'un nouveau message
    socket.on("new_message", (msg) => {
        const panel = document.querySelector(`#discussion-${msg.channel_id}`)
        const p = document.createElement("p")
        p.innerHTML = `<strong>${msg.author}</strong> : ${msg.content}`
        panel.querySelector("form").before(p)
    })
})();