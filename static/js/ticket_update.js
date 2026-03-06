const modifBtns = document.querySelectorAll('.modif_ticket_buton');
const dialog_update = document.getElementById('update-ticket-dialog')
let currentItemId = null
//pour modifier
modifBtns.forEach((modif) =>{
    modif.addEventListener('click', ()=> {
        currentItemId= modif.dataset.itemId;
        fetch(`/ticket/${currentItemId}/edit`, {
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
            })
    })
})

document.getElementById("update-cancel-btn").addEventListener('click', ()=>{
    dialog_update.close();
})

document.getElementById("modal-form_update").addEventListener('submit', (e) =>{
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch(`/api/task/${currentItemId}/edit`, {
        method: 'POST',
        body: formData
    })
    .then((response) => response.json())
    .then((data) => {
        if(data.success){
            dialog_update.close();
            alert("sa marche")
            location.reload();
        }
    })
    .catch((error) => {
        console.error("Erreur:", error);
    })
});