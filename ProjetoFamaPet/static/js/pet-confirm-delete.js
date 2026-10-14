document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.dataset.confirmMessage) {
        return;
    }

    if (!window.confirm(form.dataset.confirmMessage)) {
        event.preventDefault();
    }
});