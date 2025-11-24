// Parallax scrolling effect
document.addEventListener('DOMContentLoaded', function() {
    // Parallax effect for hero section
    const parallaxLayer = document.querySelector('.parallax-layer');
    const heroParallax = document.querySelector('.hero-parallax');
    
    if (parallaxLayer && heroParallax) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxSpeed = 0.5;
            const yPos = -(scrolled * parallaxSpeed);
            
            parallaxLayer.style.transform = `translateY(${yPos}px)`;
        });
    }
    
    // Animated counter for stats
    const statNumbers = document.querySelectorAll('.stat-number');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                animateCounter(entry.target);
            }
        });
    }, observerOptions);
    
    statNumbers.forEach(stat => observer.observe(stat));
    
    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add fade-in animation to sections as they come into view
    const fadeElements = document.querySelectorAll('.project-card, .coursework-card, .ai-section');
    
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        fadeObserver.observe(element);
    });
    
    // Dynamic hover effects for cards
    const cards = document.querySelectorAll('.project-card, .coursework-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        });
    });
    
    // Typing effect for AI chat preview
    const typingMessage = document.querySelector('.chat-message.typing .message-content');
    if (typingMessage) {
        let dots = 0;
        setInterval(() => {
            dots = (dots + 1) % 4;
            typingMessage.setAttribute('data-dots', '.'.repeat(dots));
        }, 500);
    }
    
    // Sticky header shadow on scroll
    const header = document.querySelector('.md-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
    
    // Add resize observer for responsive adjustments
    const resizeObserver = new ResizeObserver(entries => {
        entries.forEach(entry => {
            if (entry.target === document.body) {
                // Adjust parallax speed based on screen size
                if (window.innerWidth < 768) {
                    parallaxSpeed = 0.3;
                } else {
                    parallaxSpeed = 0.5;
                }
            }
        });
    });
    
    resizeObserver.observe(document.body);
});

// Add CSS for scrolled header
const style = document.createElement('style');
style.textContent = `
    .md-header.scrolled {
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .md-header {
        transition: box-shadow 0.3s ease;
    }
    
    @media (prefers-reduced-motion: reduce) {
        .parallax-layer {
            transform: none !important;
        }
        
        .hero-parallax {
            background-attachment: scroll;
        }
        
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
`;
document.head.appendChild(style);
