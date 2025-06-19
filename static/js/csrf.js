function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
}

document.addEventListener('DOMContentLoaded', function() {
    const token = getCSRFToken();
    if (token) {
        const csrfToken = document.querySelector('input[name="csrf_token"]');
        if (csrfToken) {
            csrfToken.value = token;
        }
        
        const { fetch: originalFetch } = window;
        window.fetch = async (...args) => {
            const [resource, config = {}] = args;
            const newConfig = {
                ...config,
                headers: {
                    ...config.headers,
                    'X-CSRFToken': token
                }
            };
            return originalFetch(resource, newConfig);
        };
        
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function() {
            this.addEventListener('load', function() {
                const csrfToken = this.getResponseHeader('X-CSRF-Token');
                if (csrfToken) {
                    const meta = document.querySelector('meta[name="csrf-token"]');
                    if (meta) {
                        meta.content = csrfToken;
                    }
                }
            });
            originalOpen.apply(this, arguments);
        };
    }
});
