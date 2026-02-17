(() => {
    const initTicketSortManager = () => {
        const form = document.querySelector('.filters form');
        if (!form) return;

        const statusSelect = form.querySelector('#status');
        const sortSelect = form.querySelector('#sort');
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
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTicketSortManager);
    } else {
        initTicketSortManager();
    }
})();