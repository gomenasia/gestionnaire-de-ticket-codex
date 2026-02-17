(() => {
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
        print('input changed, debounce submit');
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(submitFilters, 250);
    };

    [statusSelect, sortSelect].forEach((element) => {
        print('adding change listener to', element);
        if (!element) return;
        element.addEventListener('change', submitFilters);
    });

    [searchInput, authorInput].forEach((element) => {
        if (!element) return;
        element.addEventListener('input', submitWithDebounce);
        element.addEventListener('search', submitFilters);
    });
})();