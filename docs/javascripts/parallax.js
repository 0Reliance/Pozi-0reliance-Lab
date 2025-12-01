/**
 * Parallax Controller for Homelab Documentation Hub
 * Implements smooth scroll-based parallax with performance optimizations
 */

class ParallaxController {
  constructor() {
    this.layers = document.querySelectorAll('.parallax-layer');
    this.ticking = false;
    this.transformValues = new Map();
    this.intersectionObserver = null;
    this.rafId = null;
    this.lastScrollY = 0;
    this.speeds = new Map();
    this.init();
  }

  /**
   * Initialize parallax controller
   */
  init() {
    this.setupInitialPositions();
    this.setupSpeeds();
    this.addScrollListener();
    this.addResizeListener();
    this.setupIntersectionObserver();
    this.startRAF();
  }

  /**
   * Setup initial transform positions
   */
  setupInitialPositions() {
    this.layers.forEach((layer, index) => {
      const speed = parseFloat(layer.dataset.speed) || 0.5;
      this.transformValues.set(layer, 0);
      this.speeds.set(layer, speed);
    });
  }

  /**
   * Setup parallax speeds for each layer
   */
  setupSpeeds() {
    // Set speeds for actual parallax layers that exist in the HTML
    this.layers.forEach((layer, index) => {
      if (layer.classList.contains('parallax-back')) {
        this.speeds.set(layer, 0.3);
      } else if (layer.classList.contains('parallax-tech')) {
        this.speeds.set(layer, 0.5);
      } else if (layer.classList.contains('parallax-mid')) {
        this.speeds.set(layer, 0.7);
      } else {
        // Default speed for any other layers
        this.speeds.set(layer, 0.5);
      }
    });
  }

  /**
   * Add scroll event listener
   */
  addScrollListener() {
    window.addEventListener('scroll', this.onScroll.bind(this), { passive: true });
  }

  /**
   * Add resize event listener
   */
  addResizeListener() {
    window.addEventListener('resize', this.onResize.bind(this));
  }

  /**
   * Setup Intersection Observer for performance
   */
  setupIntersectionObserver() {
    if ('IntersectionObserver' in window) {
      this.intersectionObserver = new IntersectionObserver(
        this.onIntersection.bind(this),
        { threshold: [0, 0.1, 0.5, 1] }
      );

      // Observe all parallax layers
      this.layers.forEach(layer => {
        this.intersectionObserver.observe(layer);
      });
    }
  }

  /**
   * Start Request Animation Frame
   */
  startRAF() {
    const animate = () => {
      this.updateTransforms();
      this.rafId = requestAnimationFrame(animate);
    };
    
    animate();
  }

  /**
   * Stop Request Animation Frame
   */
  stopRAF() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  /**
   * Handle scroll events
   */
  onScroll() {
    if (!this.ticking) {
      this.lastScrollY = window.pageYOffset;
      this.startRAF();
    }
  }

  /**
   * Handle resize events
   */
  onResize() {
    this.updateTransforms();
  }

  /**
   * Handle intersection observer callbacks
   */
  onIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const layer = entry.target;
        const rect = layer.getBoundingClientRect();
        const visible = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (visible) {
          layer.classList.add('visible');
        } else {
          layer.classList.remove('visible');
        }
      }
    });
  }

  /**
   * Update transform values for all layers
   */
  updateTransforms() {
    const scrollY = window.pageYOffset;
    const windowHeight = window.innerHeight;
    
    this.layers.forEach((layer, index) => {
      const speed = this.speeds.get(layer) || 0.5;
      const yPos = -(scrollY * speed);
      const transform = `translate3d(0, ${yPos}px, 0)`;
      
      if (layer.style.transform !== transform) {
        layer.style.transform = transform;
        this.transformValues.set(layer, yPos);
      }
    });
    
    this.ticking = false;
  }

  /**
   * Enhanced scroll handler with performance optimizations
   */
  onScrollEnhanced() {
    const currentScrollY = window.pageYOffset;
    const scrollDelta = Math.abs(currentScrollY - this.lastScrollY);
    
    // Only update if significant scroll change
    if (scrollDelta > 1) {
      this.lastScrollY = currentScrollY;
      this.updateTransforms();
    }
  }

  /**
   * Set visibility state based on user preferences
   */
  setParallaxEnabled(enabled) {
    this.layers.forEach(layer => {
      if (enabled) {
        layer.style.willChange = 'transform';
        layer.classList.remove('parallax-disabled');
      } else {
        layer.style.willChange = 'auto';
        layer.classList.add('parallax-disabled');
      }
    });
  }

  /**
   * Update parallax speed dynamically
   */
  updateSpeed(layerIndex, speed) {
    const layer = this.layers[layerIndex];
    if (layer) {
      layer.dataset.speed = speed;
      this.speeds.set(layer, speed);
    }
  }

  /**
   * Add floating element to hero section
   */
  addFloatingElement() {
    const hero = document.querySelector('.hero-parallax');
    if (hero) {
      const floatingNode = document.createElement('div');
      floatingNode.className = 'floating-node';
      floatingNode.style.css = `
        position: absolute;
        width: 30px;
        height: 30px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        border-radius: 50%;
        top: 20%;
        left: ${10 + Math.random() * 60}%;
        animation: float 6s infinite ease-in-out;
        z-index: 5;
      `;
      
      hero.appendChild(floatingNode);
      
      // Add more floating nodes
      for (let i = 0; i < 3; i++) {
        const node = document.createElement('div');
        node.className = 'floating-node';
        node.style.css = `
          position: absolute;
          width: ${15 + Math.random() * 15}px;
          height: ${15 + Math.random() * 15}px;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
          border-radius: 50%;
          top: ${10 + Math.random() * 50}%;
          left: ${5 + Math.random() * 70}%;
          animation: float ${8 + Math.random() * 4}s infinite ease-in-out;
          animation-delay: ${Math.random() * 2}s;
          z-index: ${4 - i};
        `;
        
        hero.appendChild(node);
      }
    }
  }

/**
 * CSS Animations
 */
const style = document.createElement('style');
style.textContent = `
  @keyframes float {
    0%, 100% { transform: translateY(0) translateX(0); }
    33% { transform: translateY(-10px) translateX(30px); }
    66% { transform: translateY(0) translateX(-30px); }
  }
  
  .floating-node {
    animation: float 6s infinite ease-in-out;
  }
`;
document.head.appendChild(style);

// Initialize parallax when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const parallax = new ParallaxController();
  parallax.addFloatingElement();
});

// Export for potential external use
window.ParallaxController = ParallaxController;
