  // Validación de fortaleza de contraseña
        const passwordInput = document.getElementById('password');
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');

        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[^a-zA-Z0-9]/)) strength++;

            strengthFill.className = 'strength-fill';
            
            if (strength === 0 || strength === 1) {
                strengthFill.classList.add('weak');
                strengthText.textContent = 'Contraseña débil';
            } else if (strength === 2 || strength === 3) {
                strengthFill.classList.add('medium');
                strengthText.textContent = 'Contraseña media';
            } else {
                strengthFill.classList.add('strong');
                strengthText.textContent = 'Contraseña fuerte';
            }
        });

        // Validación del formulario
        document.getElementById('registerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            let isValid = true;
            
            // Limpiar errores previos
            document.querySelectorAll('.error-message').forEach(el => {
                el.style.display = 'none';
            });
            document.querySelectorAll('.form-control').forEach(el => {
                el.classList.remove('error');
            });

            // Validar email
            const email = document.getElementById('email');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                showError('email', 'Ingresa un correo válido');
                isValid = false;
            }

            // Validar contraseñas
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirmPassword');
            
            if (password.value.length < 8) {
                showError('password', 'La contraseña debe tener al menos 8 caracteres');
                isValid = false;
            }

            if (password.value !== confirmPassword.value) {
                showError('confirmPassword', 'Las contraseñas no coinciden');
                isValid = false;
            }

            // Validar términos
            const terms = document.getElementById('terms');
            if (!terms.checked) {
                alert('Debes aceptar los términos y condiciones');
                isValid = false;
            }

            if (isValid) {
                // Aquí conectarías con tu backend Django
                const formData = new FormData(this);
                console.log('Registro exitoso:', Object.fromEntries(formData));
                
                // Ejemplo de integración con Django
                // fetch('/api/register/', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //     },
                //     body: JSON.stringify(Object.fromEntries(formData))
                // })
                // .then(response => response.json())
                // .then(data => {
                //     if (data.success) {
                //         window.location.href = '/login/';
                //     }
                // });

                alert('¡Registro exitoso! (Este es un demo)');
            }
        });

        function showError(fieldName, message) {
            const field = document.getElementById(fieldName);
            const error = document.getElementById(fieldName + 'Error');
            
            field.classList.add('error');
            error.textContent = message;
            error.style.display = 'block';
        }

        // Validación en tiempo real del usuario
        document.getElementById('username').addEventListener('blur', function() {
            if (this.value.length < 4) {
                showError('username', 'El usuario debe tener al menos 4 caracteres');
            }
        });