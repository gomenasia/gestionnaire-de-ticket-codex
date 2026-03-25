const name_btns = document.querySelectorAll('button.list');

name_btns.forEach(btn => {
    btn.addEventListener('click', (event) => {
        event.stopPropagation();
        
        const menu = btn.nextElementSibling;
        const isOpen = !menu.classList.contains('collapsed'); // true = actuellement visible

        // Ferme tous
        document.querySelectorAll('.names').forEach(m => {
            m.classList.add('collapsed');
        });

        // Ouvre uniquement si c'était fermé
        if (!isOpen) {
            menu.classList.remove('collapsed');
        }
    });
});

document.addEventListener('click', () => {
    document.querySelectorAll('.names').forEach(m => m.classList.add('collapsed'));
});

// Option : écouter sur .list directement
