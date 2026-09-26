/**
 * Authentication Module
 * Handles client-side validation and API communication for Login and Register pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const alertBox = document.getElementById('auth-alert');

    function showAlert(msg) {
        if (!alertBox) return;
        alertBox.textContent = msg;
        alertBox.style.display = 'flex';
    }

    function hideAlert() {
        if (!alertBox) return;
        alertBox.style.display = 'none';
    }

    // Handle User Registration
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideAlert();

            const name = document.getElementById('reg-name').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm-password').value;
            const submitBtn = document.getElementById('btn-submit-register');

            if (password.length < 6) {
                showAlert('Password must be at least 6 characters long.');
                return;
            }

            if (password !== confirmPassword) {
                showAlert('Passwords do not match. Please re-enter.');
                return;
            }

            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name,
                        email,
                        password,
                        confirm_password: confirmPassword
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    showAlert(data.error || 'Registration failed. Please try again.');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                    return;
                }

                showToast('Registration successful! Redirecting to Dashboard...', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 800);

            } catch (err) {
                showAlert('Network error. Unable to connect to server.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Handle User Login
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideAlert();

            const email = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;
            const submitBtn = document.getElementById('btn-submit-login');

            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    showAlert(data.error || 'Invalid credentials. Please verify your email and password.');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                    return;
                }

                showToast('Login successful! Redirecting to Dashboard...', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 600);

            } catch (err) {
                showAlert('Network error. Unable to connect to server.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }
});
