

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize all dropdowns using Bootstrap 5 syntax
    var dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    var dropdownList = dropdownElementList.map(function(dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Ensure proper dropdown positioning in tables
    document.addEventListener('shown.bs.dropdown', function(e) {
        // Get the dropdown menu
        const dropdown = e.target.querySelector('.dropdown-menu');
        if (!dropdown) return;
        
        // Check if dropdown is in a table cell
        const cell = e.target.closest('td');
        if (!cell) return;
        
        // Fix possible overflow issues
        const tableRect = cell.closest('.table-responsive')?.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        
        if (tableRect) {
            // Ensure dropdown stays within table bounds
            if (dropdownRect.right > tableRect.right) {
                dropdown.classList.add('dropdown-menu-end');
            }
            
            if (dropdownRect.bottom > window.innerHeight) {
                dropdown.style.transform = `translateY(-${dropdownRect.height}px)`;
            }
        }
    });

    // Handle form confirmation dialogs
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    const currentLocation = location.href;
    const menuItems = document.querySelectorAll('.nav-link');
    menuItems.forEach(item => {
        if (item.href === currentLocation) {
            item.classList.add('active');
            item.setAttribute('aria-current', 'page');
        }
    });

    const datepickers = document.querySelectorAll('.datepicker');
    if (datepickers.length > 0) {
        datepickers.forEach(input => {
            new Datepicker(input, {
                format: 'yyyy-mm-dd',
                autoclose: true,
                todayHighlight: true
            });
        });
    }

    document.addEventListener('click', function(e) {
        if (e.target.matches('.add-field')) {
            e.preventDefault();
            const container = e.target.closest('.dynamic-fields');
            const template = container.querySelector('.field-template');
            const newField = template.cloneNode(true);
            newField.classList.remove('field-template', 'd-none');
            newField.innerHTML = newField.innerHTML.replace(/__prefix__/g, container.dataset.count);
            container.insertBefore(newField, e.target);
            container.dataset.count = parseInt(container.dataset.count) + 1;
        }

        if (e.target.matches('.remove-field')) {
            e.preventDefault();
            const field = e.target.closest('.dynamic-field');
            if (field) {
                field.remove();
            }
        }
    });

    // Handle form submissions with data-confirm
    document.addEventListener('submit', function(e) {
        const form = e.target;
        
        // Handle confirmation dialogs
        if (form.hasAttribute('data-confirm') && !confirm(form.getAttribute('data-confirm'))) {
            e.preventDefault();
            return false;
        }
        
        // Handle AJAX forms
        if (form.hasAttribute('data-ajax')) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : '';
            
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            
            fetch(form.action, {
                method: form.method,
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': form.querySelector('input[name="_csrf_token"]')?.value || ''
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return {};
                }
                return response.json();
            })
            .then(data => {
                if (data && data.redirect) {
                    window.location.href = data.redirect;
                } else if (data && data.message) {
                    showAlert(data.message, data.status || 'success');
                    // Close the modal if form was in a modal
                    const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
                    if (modal) {
                        modal.hide();
                    }
                    // Reload the page to reflect changes
                    setTimeout(() => window.location.reload(), 1500);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred. Please try again.', 'danger');
                return false;
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            });
        }});
    });

// Function to show alert messages
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.alerts-container') || document.body;
    container.prepend(alert);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

togglePasswordVisibility = (inputId, toggleId) => {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = document.getElementById(toggleId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
};
