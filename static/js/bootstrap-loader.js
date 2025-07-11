/**
 * Bootstrap Loader - Ensures Bootstrap JS is always available
 */
(function() {
    function ensureBootstrapLoaded() {
        // Check if Bootstrap is already loaded
        if (typeof bootstrap !== 'undefined') {
            console.log('Bootstrap is loaded properly');
            return true;
        }
        
        console.warn('Bootstrap JS not found! Attempting to load it manually...');
        
        // Create a script element to load Bootstrap
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
        script.integrity = 'sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz';
        script.crossOrigin = 'anonymous';
        
        // Add it to the document
        document.head.appendChild(script);
        
        // Return false as Bootstrap isn't loaded yet
        return false;
    }
    
    // Try to load Bootstrap immediately
    const isLoaded = ensureBootstrapLoaded();
    
    // If not loaded, check again when the window loads
    if (!isLoaded) {
        window.addEventListener('load', ensureBootstrapLoaded);
    }
})();
