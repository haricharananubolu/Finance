/**
 * ALTO - Core JavaScript Utilities
 * Handles mobile sidebar, modals, alert auto-dismiss, and form interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.querySelector('.app-sidebar');

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== mobileToggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // 2. Alert Dismissal
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // Auto-dismiss success flash messages after 5 seconds
  setTimeout(() => {
    document.querySelectorAll('.alert-success').forEach(alert => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    });
  }, 5000);

  // 3. Modal System
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  };

  // Close modal on click outside box or pressing Escape
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(modal => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      });
    }
  });

  // 4. Dynamic Transaction Category Switcher
  const typeSelect = document.getElementById('transaction_type');
  const categorySelect = document.getElementById('category');

  const incomeCategories = [
    'Salary',
    'Freelance / Consulting',
    'Investments & Dividends',
    'Allowance / Stipend',
    'Business / Side Hustle',
    'Gifts',
    'Refunds & Cashbacks',
    'Other Income'
  ];

  const expenseCategories = [
    'Housing & Rent',
    'Groceries & Food',
    'Dining Out & Cafes',
    'Transportation & Fuel',
    'Utilities & Bills',
    'Healthcare & Medical',
    'Education & Books',
    'Entertainment & Subscriptions',
    'Shopping & Personal Care',
    'Travel & Vacation',
    'Debt & Loans',
    'Investments & Savings',
    'Other Expense'
  ];

  if (typeSelect && categorySelect) {
    function updateCategories() {
      const selectedType = typeSelect.value;
      const currentCategory = categorySelect.getAttribute('data-selected') || categorySelect.value;
      const categories = selectedType === 'income' ? incomeCategories : expenseCategories;

      categorySelect.innerHTML = '';
      categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat;
        if (cat === currentCategory) {
          opt.selected = true;
        }
        categorySelect.appendChild(opt);
      });
    }

    typeSelect.addEventListener('change', updateCategories);
    // Initialize on page load if category is not already set
    if (!categorySelect.value) {
      updateCategories();
    }
  }

  // 5. Delete Confirmation Modal Helper
  window.confirmDelete = function(formId, itemName) {
    const itemSpan = document.getElementById('deleteItemName');
    if (itemSpan) itemSpan.textContent = itemName;
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (confirmBtn) {
      confirmBtn.onclick = function() {
        document.getElementById(formId).submit();
      };
    }
    openModal('deleteConfirmModal');
  };
});
