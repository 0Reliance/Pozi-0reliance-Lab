---
title: Homelab Documentation Hub
description: Your comprehensive resource for homelab projects and technical documentation
---

<!-- Hero Section with Multi-Layer Parallax -->
<div class="hero-parallax">
  <!-- Background layer - slowest movement -->
  <div class="parallax-layer parallax-back" data-speed="0.3" style="background-image: url('images/parallax/hero-bg.svg');"></div>
  
  <!-- Tech pattern layer - slow movement -->
  <div class="parallax-layer parallax-tech" data-speed="0.5" style="background-image: url('images/parallax/tech-pattern.svg');"></div>
  
  <!-- Midground layer - medium movement -->
  <div class="parallax-layer parallax-mid" data-speed="0.7" style="background-image: url('images/parallax/midground.svg');"></div>
  
  <!-- Hero content overlay -->
  <div class="hero-content">
    <h1 class="hero-title">Homelab Documentation Hub</h1>
    <p class="hero-subtitle">Empowering your technical journey with AI-powered documentation</p>
    <div class="hero-buttons">
      <a href="#explore" class="md-button md-button--primary">Explore Projects</a>
      <a href="/admin" class="md-button md-button--secondary">Admin Portal</a>
    </div>
  </div>
</div>

<!-- Quick Stats Section -->
<div class="stats-section">
  <div class="stats-grid">
    <div class="stat-item">
      <div class="stat-number" data-target="50">0</div>
      <div class="stat-label">Homelab Projects</div>
    </div>
    <div class="stat-item">
      <div class="stat-number" data-target="100">0</div>
      <div class="stat-label">Course Materials</div>
    </div>
    <div class="stat-item">
      <div class="stat-number" data-target="25">0</div>
      <div class="stat-label">Tutorials</div>
    </div>
    <div class="stat-item">
      <div class="stat-number" data-target="99">0</div>
      <div class="stat-label">AI Generated</div>
    </div>
  </div>
</div>

<!-- Featured Projects Section -->
<section id="explore" class="featured-section">
  <div class="section-header">
    <h2>Featured Homelab Projects</h2>
    <p>Explore our comprehensive collection of homelab setups and configurations</p>
  </div>
  
  <div class="project-grid">
    <div class="project-card">
      <div class="project-icon">🌐</div>
      <h3>Network Infrastructure</h3>
      <p>Complete network setup with routing, switching, and security configurations</p>
      <a href="homelab/network/" class="project-link">Explore Network Setup →</a>
    </div>
    
    <div class="project-card">
      <div class="project-icon">💾</div>
      <h3>Storage Systems</h3>
      <p>NAS configurations, backup strategies, and data recovery solutions</p>
      <a href="homelab/storage/" class="project-link">Explore Storage →</a>
    </div>
    
    <div class="project-card">
      <div class="project-icon">🐳</div>
      <h3>Virtualization</h3>
      <p>Proxmox, Docker, and Kubernetes cluster management</p>
      <a href="homelab/virtualization/" class="project-link">Explore Virtualization →</a>
    </div>
    
    <div class="project-card">
      <div class="project-icon">📊</div>
      <h3>Monitoring</h3>
      <p>Grafana dashboards, Prometheus setup, and alert management</p>
      <a href="homelab/monitoring/" class="project-link">Explore Monitoring →</a>
    </div>
  </div>
</section>

<!-- Coursework Section -->
<section class="coursework-section">
  <div class="section-header">
    <h2>Coursework Materials</h2>
    <p>Comprehensive study materials for computer science and IT courses</p>
  </div>
  
  <div class="coursework-grid">
    <div class="coursework-card">
      <div class="coursework-icon">💻</div>
      <h3>Computer Science</h3>
      <p>Data structures, algorithms, and database systems</p>
      <a href="coursework/cs/" class="coursework-link">Study CS →</a>
    </div>
    
    <div class="coursework-card">
      <div class="coursework-icon">🔌</div>
      <h3>Network Engineering</h3>
      <p>TCP/IP fundamentals, security, and wireless networks</p>
      <a href="coursework/networking/" class="coursework-link">Study Networking →</a>
    </div>
    
    <div class="coursework-card">
      <div class="coursework-icon">⚙️</div>
      <h3>System Administration</h3>
      <p>Linux, Windows Server, and automation scripting</p>
      <a href="coursework/sysadmin/" class="coursework-link">Study SysAdmin →</a>
    </div>
  </div>
</section>

<!-- AI Assistant Section -->
<section class="ai-section">
  <div class="ai-content">
    <div class="ai-text">
      <h2>🤖 AI-Powered Content Management</h2>
      <p>Our intelligent AI assistant helps create, organize, and maintain all documentation. Simply describe what you need, and the AI will generate properly formatted content, update navigation, and ensure consistency across the site.</p>
      <div class="ai-features">
        <div class="ai-feature">
          <span class="ai-feature-icon">✨</span>
          <span>Automated content generation</span>
        </div>
        <div class="ai-feature">
          <span class="ai-feature-icon">🔄</span>
          <span>Smart navigation updates</span>
        </div>
        <div class="ai-feature">
          <span class="ai-feature-icon">📝</span>
          <span>Content formatting and styling</span>
        </div>
        <div class="ai-feature">
          <span class="ai-feature-icon">🔍</span>
          <span>SEO optimization</span>
        </div>
      </div>
      <a href="/admin" class="md-button md-button--primary">Try AI Assistant</a>
    </div>
    <div class="ai-visual">
      <div class="ai-chat-preview">
        <div class="chat-message ai-message">
          <div class="message-content">How can I help you create documentation today?</div>
        </div>
        <div class="chat-message user-message">
          <div class="message-content">Create a guide for setting up a home NAS</div>
        </div>
        <div class="chat-message ai-message typing">
          <div class="message-content">Generating comprehensive NAS setup guide...</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Quick Links -->
<section class="quick-links">
  <div class="quick-links-grid">
    <a href="guides/getting-started.md" class="quick-link">
      <span class="quick-link-icon">🚀</span>
      <span class="quick-link-text">Getting Started</span>
    </a>
    <a href="guides/best-practices.md" class="quick-link">
      <span class="quick-link-icon">✅</span>
      <span class="quick-link-text">Best Practices</span>
    </a>
    <a href="guides/troubleshooting.md" class="quick-link">
      <span class="quick-link-icon">🔧</span>
      <span class="quick-link-text">Troubleshooting</span>
    </a>
    <a href="guides/security.md" class="quick-link">
      <span class="quick-link-icon">🔒</span>
      <span class="quick-link-text">Security</span>
    </a>
    <a href="about/contributing.md" class="quick-link">
      <span class="quick-link-icon">🤝</span>
      <span class="quick-link-text">Contributing</span>
    </a>
    <a href="api.md" class="quick-link">
      <span class="quick-link-icon">🔌</span>
      <span class="quick-link-text">API Reference</span>
    </a>
  </div>
</section>
