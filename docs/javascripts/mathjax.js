// MathJax configuration for Homelab Docs
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true
    },
    options: {
        ignoreHtmlClass: 'tex2jax_ignore',
        processHtmlClass: 'tex2jax_process'
    },
    startup: {
        ready: () => {
            console.log('MathJax is loaded, but not yet initialized');
            MathJax.startup.defaultReady();
            MathJax.startup.promise.then(() => {
                console.log('MathJax initial typesetting complete');
            });
        }
    }
};

// Load MathJax dynamically
(function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    script.async = true;
    document.head.appendChild(script);
})();
