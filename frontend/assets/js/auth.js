// auth.js

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const roleSelect = document.getElementById('regRole');
    const supplierIdGroup = document.getElementById('supplierIdGroup');
  
    const apiBase = 'http://localhost:5000/api/auth'; // Adjust if hosted differently
  
    // Toggle Supplier ID field
    if (roleSelect) {
      roleSelect.addEventListener('change', () => {
        supplierIdGroup.style.display = (roleSelect.value === 'supplier') ? 'block' : 'none';
      });
    }
  
    // Login Submit
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
  
        const res = await fetch(`${apiBase}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
  
        const data = await res.json();
        if (data.success) {
          localStorage.setItem('token', data.access_token);
          const role = data.user.role;
          // Redirect based on role
          switch (role) {
            case 'supply_chain_manager':
              window.location.href = '/frontend/supply_chain_manager/dashboard.html';
              break;
            case 'warehouse_team':
              window.location.href = '/frontend/warehouse/warehouse_dashboard.html';
              break;
            case 'procurement_officer':
              window.location.href = '/frontend/procurement/dashboard.html';
              break;
            case 'supplier':
              window.location.href = '/supplier/dashboard.html';
              break;
            case 'sales_officer':
              window.location.href = '/sales_officer/dashboard.html';
              break;
            default:
              alert('Unknown role!');
          }
        } else {
          document.getElementById('loginMsg').innerText = data.message || 'Login failed';
        }
      });
    }
  
    // Register Submit
    if (registerForm) {
      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;
        const supplier_id = document.getElementById('supplierId').value;
  
        const payload = {
          username,
          email,
          password,
          role
        };
  
        if (role === 'supplier') {
          payload.supplier_id = supplier_id;
        }
  
        const res = await fetch(`${apiBase}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
  
        const data = await res.json();
        if (data.success) {
          alert('Registration successful! Please log in.');
          window.location.href = 'login.html';
        } else {
          document.getElementById('registerMsg').innerText = data.message || 'Registration failed';
        }
      });
    }
  });
  