// Homelab Documentation Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeScrollProgress();
    initializeBackToTop();
    initializeHeroSection();
    initializeStatsAnimation();
    initializeSearchEnhancements();
    initializeThemeCustomizations();
    initializeAnalytics();
});

// Scroll Progress Bar
function initializeScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    });
}

// Back to Top Button
function initializeBackToTop() {
    const backToTopButton = document.createElement('button');
    backToTopButton.className = 'back-to-top';
    backToTopButton.innerHTML = '↑';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    backToTopButton.setAttribute('title', 'Back to top');
    document.body.appendChild(backToTopButton);

    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });

    // Scroll to top when clicked
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Hero Section Parallax Effect
function initializeHeroSection() {
    const heroParallax = document.querySelector('.hero-parallax');
    if (!heroParallax) return;

    let ticking = false;

    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = heroParallax.querySelectorAll('.hero-content, .hero-title, .hero-subtitle');
        
        parallaxElements.forEach((element, index) => {
            const speed = 0.5 + (index * 0.1);
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });

        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            window.requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);

    // Initialize hero content animations
    animateHeroContent();
}

// Animate hero content on load
function animateHeroContent() {
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroButtons = document.querySelector('.hero-buttons');

    if (heroTitle) {
        heroTitle.classList.add('fade-in');
        heroTitle.style.animationDelay = '0.2s';
    }

    if (heroSubtitle) {
        heroSubtitle.classList.add('fade-in');
        heroSubtitle.style.animationDelay = '0.6s';
    }

    if (heroButtons) {
        heroButtons.classList.add('fade-in');
        heroButtons.style.animationDelay = '1s';
    }
}

// Animate Statistics Numbers
function initializeStatsAnimation() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                animateNumber(entry.target);
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);

    statNumbers.forEach(stat => observer.observe(stat));
}

function animateNumber(element) {
    const finalValue = parseInt(element.textContent);
    const duration = 2000; // 2 seconds
    const steps = 60;
    const stepValue = finalValue / steps;
    let currentValue = 0;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        currentValue = Math.floor(stepValue * step);
        element.textContent = currentValue;

        if (step >= steps) {
            element.textContent = finalValue;
            clearInterval(timer);
        }
    }, duration / steps);
}

// Search Enhancements
function initializeSearchEnhancements() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.blur();
            }
        }
    });

    // Add search result highlighting
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.target.classList.contains('md-search-result')) {
                highlightSearchTerms();
            }
        });
    });

    const searchResults = document.querySelector('.md-search-result');
    if (searchResults) {
        observer.observe(searchResults, { childList: true, subtree: true });
    }
}

function highlightSearchTerms() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;

    const searchTerm = searchInput.value.trim();
    if (!searchTerm) return;

    const searchResults = document.querySelectorAll('.md-search-result__teaser');
    searchResults.forEach(result => {
        const text = result.textContent;
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        result.innerHTML = text.replace(regex, '<mark>$1</mark>');
    });
}

// Theme Customizations
function initializeThemeCustomizations() {
    // Add theme transition
    const themeToggle = document.querySelector('[data-md-component="palette"]');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }

    // Add smooth scrolling for all anchor links
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

    // Add copy-to-clipboard for code blocks
    addCopyButtons();
}

function addCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre[class*="language-"]');
    
    codeBlocks.forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        
        // Style the button
        button.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: var(--md-accent-fg-color);
            color: white;
            border: none;
            border-radius: 0.25rem;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease;
            z-index: 1;
        `;

        // Make code block relative for positioning
        block.style.position = 'relative';
        block.appendChild(button);

        // Show button on hover
        block.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });

        block.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });

        // Handle copy functionality
        button.addEventListener('click', async () => {
            const code = block.querySelector('code');
            const text = code.textContent;

            try {
                await navigator.clipboard.writeText(text);
                button.textContent = 'Copied!';
                button.style.background = '#4caf50';
                
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.background = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
                button.textContent = 'Failed';
                button.style.background = '#f44336';
                
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.background = '';
                }, 2000);
            }
        });
    });
}

// Analytics and Tracking
function initializeAnalytics() {
    // Track page view
    trackPageView();

    // Track external link clicks
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        link.addEventListener('click', (e) => {
            trackEvent('external_link', 'click', link.href);
        });
    });

    // Track file downloads
    document.querySelectorAll('a[href$=".pdf"], a[href$=".zip"], a[href$=".tar.gz"]').forEach(link => {
        link.addEventListener('click', (e) => {
            trackEvent('download', 'click', link.href);
        });
    });

    // Track search queries
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    trackEvent('search', 'query', query);
                }, 1000);
            }
        });
    }
}

function trackPageView() {
    // This would integrate with your analytics service
    // For now, just log to console
    console.log('Page view:', window.location.pathname);
    
    // Example: Google Analytics
    // if (typeof gtag !== 'undefined') {
    //     gtag('config', 'GA_MEASUREMENT_ID', {
    //         page_path: window.location.pathname
    //     });
    // }
}

function trackEvent(category, action, label) {
    // This would integrate with your analytics service
    // For now, just log to console
    console.log('Event:', { category, action, label });
    
    // Example: Google Analytics
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', action, {
    //         event_category: category,
    //         event_label: label
    //     });
    // }
}

// Utility Functions

// Debounce function to limit how often a function can be called
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function to limit how often a function can be called
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Get theme colors
function getThemeColors() {
    const styles = getComputedStyle(document.documentElement);
    return {
        primary: styles.getPropertyValue('--md-primary-fg-color').trim(),
        accent: styles.getPropertyValue('--md-accent-fg-color').trim(),
        background: styles.getPropertyValue('--md-default-bg-color').trim(),
        text: styles.getPropertyValue('--md-default-fg-color').trim()
    };
}

// Export functions for potential external use
window.homelabDocs = {
    isInViewport,
    getThemeColors,
    debounce,
    throttle,
    trackEvent,
    trackPageView
};

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            console.log(`Page load time: ${loadTime}ms`);
            
            // Track performance if needed
            trackEvent('performance', 'page_load', `${loadTime}ms`);
        }
    });
}

// Service Worker registration (for offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Error handling
window.addEventListener('error', (e) => {
    console.error('JavaScript error:', e.error);
    trackEvent('error', 'javascript', e.message);
});

// Handle CSP violations
if (document.securityPolicy && document.securityPolicy.allowsInlineScript) {
    console.log('Content Security Policy is active');
}
