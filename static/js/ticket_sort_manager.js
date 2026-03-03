(() => {
    const form = document.querySelector('.filters form');
    if (!form) return;

    const statusSelect = form.querySelector('#status');
    const sortSelect = form.querySelector('#sort');
    const searchInput = form.querySelector('#q');
    const authorInput = form.querySelector('#author');

    const tickets = document.querySelectorAll('article.ticket');

    tickets.forEach((ticket) => {
        const update_status = ticket.querySelector('[id^="update_status"]');
        const select_status_update = update_status ? update_status.querySelector('[id^="status_update_select"]') : null;

        if (select_status_update) {
            select_status_update.addEventListener('change', () => {
                update_status.requestSubmit
                    ? update_status.requestSubmit()
                    : update_status.submit();
            });
        }
    });

    
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
        debounceTimer = window.setTimeout(submitFilters, 750);
    };

    [statusSelect, sortSelect].forEach((element) => {
        if (!element) return;
        element.addEventListener('change', submitFilters);
    });

    [searchInput, authorInput].forEach((element) => {
        if (!element) return;
        element.addEventListener('input', submitWithDebounce);
        element.addEventListener('search', submitFilters);
    });
})();