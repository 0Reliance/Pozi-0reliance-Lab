/**
 * Enhanced Documentation JavaScript - Usability & UX Improvements
 */

// === Reading Progress Bar ===
function initReadingProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + '%';
    });
}

// === Breadcrumb Navigation ===
function generateBreadcrumbs() {
    const pathParts = window.location.pathname.split('/').filter(part => part);
    if (pathParts.length <= 1) return; // Skip if at root

    const breadcrumbContainer = document.createElement('nav');
    breadcrumbContainer.className = 'breadcrumb';
    
    // Add home link
    const homeLink = document.createElement('a');
    homeLink.href = '/';
    homeLink.textContent = '🏠 Home';
    breadcrumbContainer.appendChild(homeLink);

    // Add path parts
    let currentPath = '';
    pathParts.forEach((part, index) => {
        currentPath += '/' + part;
        
        const separator = document.createElement('span');
        separator.className = 'separator';
        separator.textContent = ' › ';
        breadcrumbContainer.appendChild(separator);

        if (index === pathParts.length - 1) {
            // Current page
            const currentPage = document.createElement('span');
            currentPage.textContent = formatPageTitle(part);
            breadcrumbContainer.appendChild(currentPage);
        } else {
            // Parent page
            const link = document.createElement('a');
            link.href = currentPath;
            link.textContent = formatPageTitle(part);
            breadcrumbContainer.appendChild(link);
        }
    });

    // Insert breadcrumb at the top of content
    const content = document.querySelector('.md-content');
    if (content) {
        content.insertBefore(breadcrumbContainer, content.firstChild);
    }
}

function formatPageTitle(part) {
    return part
        .replace(/-/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
        .replace('.html', '');
}

// === Enhanced Code Blocks ===
function enhanceCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre[data-linenos] .highlight');
    
    codeBlocks.forEach((block, index) => {
        // Add copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = '📋 Copy';
        copyButton.setAttribute('data-copy-index', index);
        
        // Add language indicator
        const codeElement = block.querySelector('code');
        const language = codeElement ? detectLanguage(codeElement) : 'text';
        
        const langIndicator = document.createElement('div');
        langIndicator.className = 'language-indicator';
        langIndicator.textContent = language;
        
        block.style.position = 'relative';
        block.appendChild(langIndicator);
        block.appendChild(copyButton);
        
        // Add copy functionality
        copyButton.addEventListener('click', () => {
            const text = codeElement ? codeElement.textContent : block.textContent;
            copyToClipboard(text, copyButton);
        });
    });
}

function detectLanguage(codeElement) {
    const classes = codeElement.className.split(' ');
    for (const cls of classes) {
        if (cls.startsWith('language-')) {
            return cls.replace('language-', '');
        }
    }
    
    // Try to detect from filename in comments
    const text = codeElement.textContent;
    const filenameMatch = text.match(/\/\*\s*([^*\/\s]+\.[a-z]+)\s*\*\/|\/\/\s*([^*\/\s]+\.[a-z]+)/);
    if (filenameMatch) {
        const filename = filenameMatch[1] || filenameMatch[2];
        const ext = filename.split('.').pop();
        return ext;
    }
    
    return 'text';
}

function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = '✅ Copied!';
        button.style.background = 'var(--md-accent-fg-color)';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        button.textContent = '❌ Failed';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}

// === Table of Contents Enhancements ===
function enhanceTableOfContents() {
    const toc = document.querySelector('.md-nav--secondary');
    if (!toc) return;

    // Add "Contents" header if missing
    const existingHeader = toc.querySelector('.md-nav__title');
    if (!existingHeader) {
        const header = document.createElement('div');
        header.className = 'md-nav__title';
        header.textContent = '📋 Contents';
        toc.insertBefore(header, toc.firstChild);
    }

    // Add expand/collapse functionality for mobile
    if (window.innerWidth <= 768) {
        toc.classList.add('md-nav--secondary--collapsed');
        
        const toggle = document.createElement('button');
        toggle.className = 'toc-toggle';
        toggle.textContent = '📋 Contents';
        toggle.style.cssText = `
            background: var(--md-accent-fg-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            cursor: pointer;
            font-weight: 600;
        `;
        
        toggle.addEventListener('click', () => {
            toc.classList.toggle('md-nav--secondary--collapsed');
        });
        
        toc.parentElement.insertBefore(toggle, toc);
    }
}

// === Interactive Elements ===
function addInteractiveElements() {
    // Add "Back to Top" button
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.textContent = '↑';
    backToTop.title = 'Back to Top';
    document.body.appendChild(backToTop);

    // Show/hide based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    // Smooth scroll to top
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Add external link indicators
    const links = document.querySelectorAll('a[href^="http"]');
    links.forEach(link => {
        if (!link.hostname.includes(window.location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
            
            // Add external link icon if not already present
            if (!link.textContent.includes('↗') && !link.querySelector('img')) {
                const icon = document.createElement('span');
                icon.textContent = ' ↗';
                icon.style.fontSize = '0.8em';
                icon.style.opacity = '0.7';
                link.appendChild(icon);
            }
        }
    });
}

// === Search Enhancements ===
function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;

    // Add search shortcuts
    searchInput.addEventListener('keydown', (e) => {
        // Escape to clear search
        if (e.key === 'Escape') {
            searchInput.value = '';
            searchInput.blur();
        }
        
        // Ctrl+K to focus search
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
        }
    });

    // Global shortcut for search
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'k' && document.activeElement !== searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    });
}

// === Task Progress Indicators ===
function enhanceTaskLists() {
    const taskLists = document.querySelectorAll('.task-list');
    
    taskLists.forEach(list => {
        const tasks = list.querySelectorAll('li');
        const total = tasks.length;
        const completed = list.querySelectorAll('input[type="checkbox"]:checked').length;
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

        // Create progress indicator
        const progressContainer = document.createElement('div');
        progressContainer.className = 'task-progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        
        const progressFill = document.createElement('div');
        progressFill.className = 'progress-fill';
        progressFill.style.width = percentage + '%';
        
        const progressText = document.createElement('div');
        progressText.className = 'progress-text';
        progressText.textContent = `${completed}/${total} (${percentage}%)`;
        
        progressBar.appendChild(progressFill);
        progressContainer.appendChild(progressBar);
        progressContainer.appendChild(progressText);
        
        // Insert before the task list
        list.parentNode.insertBefore(progressContainer, list);
        
        // Update progress when checkboxes change
        list.addEventListener('change', () => {
            const newCompleted = list.querySelectorAll('input[type="checkbox"]:checked').length;
            const newPercentage = Math.round((newCompleted / total) * 100);
            
            progressFill.style.width = newPercentage + '%';
            progressText.textContent = `${newCompleted}/${total} (${newPercentage}%)`;
        });
    });
}

// === Image Enhancements ===
function enhanceImages() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // Add loading="lazy" if not present
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
        
        // Add error handling
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const errorPlaceholder = document.createElement('div');
            errorPlaceholder.textContent = '🖼️ Image not available';
            errorPlaceholder.style.cssText = `
                display: inline-block;
                padding: 1rem;
                background: var(--md-code-bg-color);
                border: 1px dashed var(--md-default-fg-color--light);
                border-radius: 4px;
                color: var(--md-default-fg-color--light);
                font-style: italic;
            `;
            this.parentNode.insertBefore(errorPlaceholder, this);
        });
        
        // Add zoom functionality for large images
        img.addEventListener('click', function() {
            if (this.naturalWidth > this.offsetWidth || this.naturalHeight > this.offsetHeight) {
                const overlay = document.createElement('div');
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.9);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    cursor: pointer;
                `;
                
                const zoomedImg = document.createElement('img');
                zoomedImg.src = this.src;
                zoomedImg.style.cssText = `
                    max-width: 90%;
                    max-height: 90%;
                    object-fit: contain;
                    border-radius: 8px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                `;
                
                overlay.appendChild(zoomedImg);
                document.body.appendChild(overlay);
                
                overlay.addEventListener('click', () => {
                    document.body.removeChild(overlay);
                });
                
                // Escape to close
                document.addEventListener('keydown', function closeOnEscape(e) {
                    if (e.key === 'Escape') {
                        document.body.removeChild(overlay);
                        document.removeEventListener('keydown', closeOnEscape);
                    }
                });
            }
        });
        
        // Add title if missing and alt text exists
        if (!img.title && img.alt) {
            img.title = img.alt;
        }
    });
}

// === Keyboard Navigation ===
function enhanceKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Skip if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Arrow key navigation for TOC
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            const toc = document.querySelector('.md-nav--primary');
            if (toc) {
                const links = toc.querySelectorAll('.md-nav__link');
                const current = toc.querySelector('.md-nav__link--active');
                
                if (current) {
                    const currentIndex = Array.from(links).indexOf(current);
                    let newIndex;
                    
                    if (e.key === 'ArrowLeft') {
                        newIndex = Math.max(0, currentIndex - 1);
                    } else {
                        newIndex = Math.min(links.length - 1, currentIndex + 1);
                    }
                    
                    if (links[newIndex]) {
                        links[newIndex].click();
                    }
                }
            }
        }
    });
}

// === Performance Monitoring ===
function initPerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
        
        console.log(`Page load time: ${loadTime}ms`);
        
        // Log slow loads
        if (loadTime > 3000) {
            console.warn('Slow page load detected:', {
                loadTime: loadTime + 'ms',
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart + 'ms',
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime + 'ms'
            });
        }
    });
}

// === Theme Enhancements ===
function enhanceTheme() {
    // Detect system theme preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Add smooth theme transitions
    document.documentElement.style.setProperty('--theme-transition', 'background-color 0.3s ease, color 0.3s ease');
    
    // Listen for theme changes
    prefersDark.addEventListener('change', (e) => {
        console.log('System theme changed:', e.matches ? 'dark' : 'light');
    });
}

// === Initialize Everything ===
function initEnhancements() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
}

function initAll() {
    console.log('🚀 Initializing documentation enhancements...');
    
    try {
        initReadingProgress();
        generateBreadcrumbs();
        enhanceCodeBlocks();
        enhanceTableOfContents();
        addInteractiveElements();
        enhanceSearch();
        enhanceTaskLists();
        enhanceImages();
        enhanceKeyboardNavigation();
        initPerformanceMonitoring();
        enhanceTheme();
        
        console.log('✅ All enhancements initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing enhancements:', error);
    }
}

// === Utility Functions ===
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

// === Export for external use ===
window.DocEnhancements = {
    init: initEnhancements,
    debounce: debounce,
    throttle: throttle,
    copyToClipboard: copyToClipboard
};

// Auto-initialize
initEnhancements();
