const upDateCheckboxes = () =>{
    //change le status des taches
    const inputElems = document.querySelectorAll('input[type="checkbox"]');
    inputElems.forEach(checkboxe => {
        checkboxe.addEventListener("click", async (e) => {
            e.stopPropagation();

            const taskId = checkboxe.dataset.taskId;
            
            fetch(`/api/task/${taskId}/status`,{
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'},
                body: JSON.stringify({status:checkboxe.checked})
            })
            .then((response) => response.json())
            .then((data)=>{
                if(data.success) {
                    location.reload();
                }else{
                    checkbox.checked = !checkbox.checked;
                }
            })
            .catch((error) =>{
                console.error("Erreur:",error)
                checkbox.checked = !checkbox.checked;
            })
        })
    });
}


//garder les details ouvert
const upDateDetails = ()=>{
    document.querySelectorAll('details').forEach(details => {
    const btn = details.querySelector('.add-task-btn');
    if (!btn) return;
    const id = btn.dataset.itemId;

    // Restaure
    if (localStorage.getItem(`details-${id}`) === 'true') {
        details.open = true;
    }

    // Sauvegarde
    details.addEventListener('toggle', () => {
        localStorage.setItem(`details-${id}`, details.open);
        });
    });
}

//progressBar
const enableProgressbar = () => {
    const progressbars = document.querySelectorAll(".progressbar")
    progressbars.forEach(bar =>{
        bar.setAttribute("role", "progressbar")
        bar.setAttribute("aria-valuenow", 0)
        bar.setAttribute("aria-live", "polite")
    })
}

upDateCheckboxes()
upDateDetails()
enableProgressbar()


