/**
 * Dropdown Fix - Force initialization of Bootstrap 5 dropdowns
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dropdown fix script loaded');
    
    // Force initialize all dropdowns on the page
    function initDropdowns() {
        console.log('Initializing dropdowns');
        var dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownElementList.forEach(function(dropdownToggleEl) {
            try {
                // Destroy existing dropdown instances to prevent conflicts
                var dropdown = bootstrap.Dropdown.getInstance(dropdownToggleEl);
                if (dropdown) {
                    dropdown.dispose();
                }
                // Create new dropdown instance
                new bootstrap.Dropdown(dropdownToggleEl);
                console.log('Initialized dropdown:', dropdownToggleEl);
            } catch (e) {
                console.error('Error initializing dropdown:', e);
            }
        });
    }
    
    // Add manual click handlers as a fallback
    function addManualHandlers() {
        console.log('Adding manual dropdown handlers');
        document.querySelectorAll('.dropdown-toggle').forEach(function(element) {
            element.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                
                var dropdownMenu = this.nextElementSibling;
                if (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu')) {
                    dropdownMenu = this.parentElement.querySelector('.dropdown-menu');
                }
                
                if (dropdownMenu) {
                    var isActive = dropdownMenu.classList.contains('show');
                    
                    // Close all other dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                        menu.classList.remove('show');
                    });
                    
                    // Toggle this dropdown
                    if (!isActive) {
                        dropdownMenu.classList.add('show');
                        
                        // Position dropdown properly for table cells
                        var rect = dropdownMenu.getBoundingClientRect();
                        var viewportWidth = window.innerWidth;
                        
                        if (rect.right > viewportWidth) {
                            dropdownMenu.classList.add('dropdown-menu-end');
                        }
                        
                        // Close when clicking outside
                        setTimeout(function() {
                            document.addEventListener('click', function closeDropdown(event) {
                                if (!dropdownMenu.contains(event.target) && !element.contains(event.target)) {
                                    dropdownMenu.classList.remove('show');
                                    document.removeEventListener('click', closeDropdown);
                                }
                            });
                        }, 0);
                    }
                }
            });
        });
    }
    
    // Run both approaches for maximum compatibility
    initDropdowns();
    addManualHandlers();
    
    // Also initialize when content changes (for dynamically loaded content)
    const observer = new MutationObserver(function(mutations) {
        initDropdowns();
        addManualHandlers();
    });
    
    // Observe changes to the DOM
    observer.observe(document.body, { childList: true, subtree: true });
});
