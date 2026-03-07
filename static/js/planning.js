
const dialog_creation = document.getElementById('task-dialog');
const dialog_update = document.getElementById('update-task-dialog')
const optionBtns = document.querySelectorAll('.option-btn');
const modifBtns = document.querySelectorAll('.modif-btn');
const suprBtns= document.querySelectorAll('.suppr-btn')
let currentItemId = null;

//MOdal de creation de tache
document.querySelectorAll('.add-task-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        currentItemId = btn.dataset.itemId;
        dialog_creation.showModal();
    });
});

document.getElementById('modal-cancel-btn').addEventListener('click', () => {
    dialog_creation.close();
});

dialog_creation.addEventListener('click', (e) => {
    if (e.target === dialog_creation) dialog_creation.close();
});

document.getElementById('modal-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch(`/planning/addTask?parent_id=${currentItemId}`, {
        method: 'POST',
        body: formData
    });
    if (response.ok) {
        dialog_creation.close();
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

//bouton option
optionBtns.forEach(btn => {
    btn.addEventListener('click', (event) => {
        event.stopPropagation(); // empêche la propagation au <summary>

        const menu = btn.nextElementSibling; // le .menu-option juste après

            // Ferme tous les autres menus
        document.querySelectorAll('.menu-option').forEach(m => {
            if (m !== menu) m.classList.add('collapse');
        });

        // Toggle celui-ci
        menu.classList.toggle('collapse');
    });
});

// Clic ailleurs = ferme tout
document.addEventListener('click', () => {
    document.querySelectorAll('.menu-option').forEach(m => m.classList.add('collapse'));
});

//modal update de task 

//pour modifier
modifBtns.forEach((modif) =>{
    modif.addEventListener('click', ()=> {
        currentItemId= modif.dataset.itemId;
        fetch(`/planning/task/${currentItemId}/update`, {
            method: 'GET',
            headers: {
                    'Content-Type': 'application/json'}
        })
        .then((response) => response.json())
            .then((data) => {
                if(data.success){
                    const  titre = document.getElementById("update-title-input");
                    titre.value = data.title;
                    const content = document.getElementById("update-content-input");
                    content.value = data.content;
                    dialog_update.showModal()
                }
            })
            .catch((error) => {
                console.error("Erreur:", error);
            })
    })
})

document.getElementById("update-cancel-btn").addEventListener('click', ()=>{
    dialog_update.close();
})

document.getElementById("modal-form_update").addEventListener('submit', (e) =>{
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch(`/planning/task/${currentItemId}/update`, {
        method: 'POST',
        body: formData
    })
    .then((response) => response.json())
    .then((data) => {
        if(data.success){
            dialog_update.close();
            location.reload();
        }
    })
    .catch((error) => {
        console.error("Erreur:", error);
    })
})

//pour supprimer
suprBtns.forEach((supr) => {
    supr.addEventListener('click', () => {
        const currentItemId = supr.dataset.itemId;
        
        fetch(`/planning/task/${currentItemId}/delete`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            
            if (data.success) {
                location.reload();
            } else {
                console.log('success = false');
            }
        })
        .catch(error => {
            console.error('Erreur catch:', error);
        });
    });
});