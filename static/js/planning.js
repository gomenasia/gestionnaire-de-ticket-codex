
const dialog = document.getElementById('task-dialog');
const optionBtns = document.querySelectorAll('.option-btn');
const modifBtns = document.querySelectorAll('.modif-btn');
const suprBtns= document.querySelectorAll('.suppr-btn')
let currentItemId = null;


document.querySelectorAll('.add-task-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        currentItemId = btn.dataset.itemId;
        dialog.showModal();
    });
});

document.getElementById('modal-cancel-btn').addEventListener('click', () => {
    dialog.close();
});

dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog.close();
});

document.getElementById('modal-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch(`/api/addTask?parent_id=${currentItemId}`, {
        method: 'POST',
        body: formData
    });
    if (response.ok) {
        dialog.close();
        location.reload();
    }
    if (response.status === 401) {
        const pop =document.getElementById('notConnected');
        const errorMsg = document.getElementById('error-message')
        const data = await response.json();
        errorMsg.textContent= data.message;
        pop.showModal();
    }
});

document.getElementById('not-connected-close-btn').addEventListener('click', () => {
    document.getElementById('notConnected').close();
});
document.getElementById('notConnected').addEventListener('close', async (e) =>{
    window.location.href = "/auth/login";
})


optionBtns.forEach(btn => {
    btn.addEventListener('click', (event) => {
        event.stopPropagation(); // empêche la propagation au <summary>

        const menu = btn.nextElementSibling; // le .menu-option juste après

            // Ferme tous les autres menus
        document.querySelectorAll('.menu-option').forEach(m => {
            if (m !== menu) m.classList.remove('active');
        });

        // Toggle celui-ci
        menu.classList.toggle('active');
    });
});

// Clic ailleurs = ferme tout
document.addEventListener('click', () => {
    document.querySelectorAll('.menu-option').forEach(m => m.classList.remove('active'));
});

