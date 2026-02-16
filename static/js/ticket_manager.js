// Synchronise les filtres de la page de gestion des tickets
// et applique le tri/filtrage instantanément.

(() => {
    const form = document.querySelector('.filters form');
    if (!form) return;

    const statusSelect = form.querySelector('#status');
    const sortSelect = form.querySelector('#sort');
    const overdueCheckbox = form.querySelector('#overdue');
    const searchInput = form.querySelector('#q');
    const authorInput = form.querySelector('#author');

    let debounceTimer;

    const submitFilters = () => {
        if (typeof form.requestSubmit === 'function') {
            form.requestSubmit();
        } else {
            form.submit();
        }
    };

    const submitWithDebounce = () => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(submitFilters, 250);
    };

    [statusSelect, sortSelect].forEach((element) => {
        if (!element) return;
        element.addEventListener('change', submitFilters);
    });

    if (overdueCheckbox) {
        overdueCheckbox.addEventListener('change', submitFilters);
    }

    [searchInput, authorInput].forEach((element) => {
        if (!element) return;
        element.addEventListener('input', submitWithDebounce);
        element.addEventListener('search', submitFilters);
    });
})();
