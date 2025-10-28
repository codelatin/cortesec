// ==================== HAMBURGER MENU FUNCTIONALITY ====================

// Variables para los elementos del DOM
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');
const navLinks = document.querySelectorAll('.nav-link');
const navButtons = document.querySelector('.nav-buttons');

// ==================== EVENTO PRINCIPAL DEL HAMBURGER ====================

// Toggle del menú hamburger
hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    
    // Prevenir scroll cuando el menú está abierto
    document.body.style.overflow = hamburger.classList.contains('active') ? 'hidden' : 'auto';
});

// ==================== CERRAR MENÚ AL HACER CLIC EN LINKS ====================

// Cerrar menú cuando se hace clic en un link de navegación
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.style.overflow = 'auto';
    });
});

// ==================== CERRAR MENÚ AL HACER CLIC EN BOTONES ====================

// Cerrar menú cuando se hace clic en botones de autenticación
const authButtons = document.querySelectorAll('.btn');
authButtons.forEach(button => {
    button.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.style.overflow = 'auto';
    });
});

// ==================== CERRAR MENÚ AL HACER CLIC FUERA ====================

// Cerrar menú cuando se hace clic fuera de él
document.addEventListener('click', (e) => {
    const isClickInsideNav = navMenu.contains(e.target);
    const isClickInsideHamburger = hamburger.contains(e.target);
    
    if (!isClickInsideNav && !isClickInsideHamburger && navMenu.classList.contains('active')) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// ==================== CERRAR MENÚ AL CAMBIAR TAMAÑO DE VENTANA ====================

// Cerrar menú cuando la ventana cambia de tamaño (de móvil a desktop)
window.addEventListener('resize', () => {
    if (window.innerWidth > 960) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// ==================== SMOOTH SCROLL PARA ANCLAS ====================

// Smooth scroll para los enlaces internos
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Solo aplicar smooth scroll si el href no es solo "#"
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ==================== EFECTO DE SCROLL EN LA NAVBAR ====================

// Cambiar estilo de navbar al hacer scroll
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 50) {
        navbar.style.boxShadow = '0 10px 35px rgba(0, 153, 255, 0.3)';
    } else {
        navbar.style.boxShadow = '0 8px 25px rgba(0, 153, 255, 0.15)';
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});

// ==================== INICIALIZACIÓN ====================

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Navbar hamburger menu inicializado correctamente');
    
    // Asegurar que el menú está cerrado al cargar
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
    document.body.style.overflow = 'auto';
});

// ==================== FUNCIONES ADICIONALES ====================

// Función para cerrar el menú programáticamente
function closeMenu() {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Función para abrir el menú programáticamente
function openMenu() {
    hamburger.classList.add('active');
    navMenu.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Función para toggle del menú
function toggleMenu() {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    
    if (hamburger.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = 'auto';
    }
}