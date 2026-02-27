const calcProgress = (detailsElement) => {
    // Cherche uniquement les <details> enfants DIRECTS
    const directChildDetails = [...detailsElement.children].filter(el => 
        el.tagName === 'DETAILS'
    );

    if (directChildDetails.length === 0) return 0;

    let total = 0;

    directChildDetails.forEach(child => {
        const checkbox = child.querySelector(':scope > summary > input[type="checkbox"]');
        const progressBar = child.querySelector(':scope > summary > .progressbar');

        if (checkbox) {
            // Tâche feuille → 100 si cochée, 0 sinon
            total += checkbox.checked ? 100 : 0;
        } else if (progressBar) {
            // Tâche avec enfants → calcul récursif
            total += calcProgress(child);
        }
    });

    return Math.round(total / directChildDetails.length);
}

const updateAllParents = (checkboxElement) => {
    // Remonte de details en details
    let current = checkboxElement.closest('details')?.parentElement?.closest('details');

    while (current) {
        const progressBar = current.querySelector(':scope > summary > .progressbar');
        if (progressBar) {
            const progress = calcProgress(current);
            const id = progressBar.getAttribute('id');

            if(progress == 100 && localStorage.getItem(`progress-${id}`) <100){
                fetch(`/api/task/${id}/status`,{
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'},
                body: JSON.stringify({status: true})
                })
                .catch((error) => {
                    console.error("Erreur:", error);
                })
            }
            if(progress < 100 && localStorage.getItem(`progress-${id}`) ==100){
                fetch(`/api/task/${id}/status`,{
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'},
                body: JSON.stringify({status: false})
                })
                .catch((error) => {
                    console.error("Erreur:", error);
                })
            }
            progressBar.setAttribute("aria-valuenow", progress);
            progressBar.style.setProperty('--progress', progress + "%");
            localStorage.setItem(`progress-${id}`, progress);
        }
        current = current.parentElement?.closest('details');
    }
}


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
            .then((data) => {
                if (data.success) {
                    updateAllParents(checkboxe);
                } else {
                    checkboxe.checked = !checkboxe.checked;
                }
            })
            .catch((error) => {
                console.error("Erreur:", error);
                checkboxe.checked = !checkboxe.checked;
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

const updateProgress = () =>{
    const progressbars = document.querySelectorAll(".progressbar")

    progressbars.forEach(progressBar =>{
        const taks_id= progressBar.getAttribute('id')

        if(localStorage.getItem(`progress-${taks_id}`) !== null){
            const progress = localStorage.getItem(`progress-${taks_id}`)
            progressBar.setAttribute("aria-valuenow", progress)
            progressBar.style.setProperty('--progress', progress + "%")
        }
    })
    
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

upDateCheckboxes();
upDateDetails();
enableProgressbar();
updateProgress();




