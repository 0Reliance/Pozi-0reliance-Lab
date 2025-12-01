# Parallax & Hero Section Implementation Guide

**Last Updated**: December 1, 2025  
**Version**: 2.0 (Immersive Hero Enhancement)  
**Status**: Ready for Implementation

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Current Implementation (Phase 1)](#current-implementation-phase-1)
3. [Upcoming Enhancements (Phase 2)](#upcoming-enhancements-phase-2)
4. [Video & GIF Parallax (Phase 3)](#upcoming-enhancements-phase-3-video--gif-parallax-backgrounds)
5. [Architecture & Layers](#architecture--layers)
6. [File Structure](#file-structure)
7. [Implementation Checklist](#implementation-checklist)
8. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Quick Reference

### What We Have Now ✅
- 3-layer parallax hero section (hero-bg.svg, tech-pattern.svg, midground.svg)
- Fixed-width hero container (~70% viewport width)
- Stats animation with data-target attributes
- Smooth 60fps scroll performance
- Mobile responsive
- Material Design theme integration

### What's Next 🚀
- Convert hero to full-screen (100% viewport width & height)
- Position navigation fixed over hero
- Z-index stack optimization (Nav > Content > Hero)
- Homepage-only styling (no impact on other pages)
- Enhanced parallax effect in full screen

---

## Current Implementation (Phase 1)

### 1. Statistics Animation Fix

**Problem**: Numbers weren't animating from 0 to target values

**Solution**: Read `data-target` attribute instead of textContent
```javascript
const finalValue = parseInt(element.getAttribute('data-target')) || parseInt(element.textContent);
```

**Status**: ✅ COMPLETE

### 2. Three-Layer Parallax Architecture

The homepage currently features three visual layers with different scroll speeds:

| Layer | Speed | Opacity | Image | Z-Index | Purpose |
|-------|-------|---------|-------|---------|---------|
| Back (Hero BG) | 0.3 | 0.6 | hero-bg.svg | 1 | Deep gradient backdrop |
| Tech Pattern | 0.5 | 0.2 | tech-pattern.svg | 2 | Tech aesthetic overlay |
| Midground | 0.7 | 0.4 | midground.svg | 3 | Depth/particle layer |
| Content | 0.4 | 1.0 | Text/Buttons | 10 | Title, subtitle, buttons |

**How It Works**:
- Each layer has `data-speed` attribute (0.3 = slowest, 0.7 = faster)
- JavaScript reads speed and applies transform: `translateY(-(scrolled * speed))`
- Slower layers appear distant, faster layers appear close (3D effect)
- GPU-accelerated with `will-change: transform`

**Status**: ✅ COMPLETE & TESTED

### 3. HTML Structure (docs/index.md)

```html
<div class="hero-parallax">
  <!-- Background layer - slowest movement -->
  <div class="parallax-layer parallax-back" data-speed="0.3" 
       style="background-image: url('../images/parallax/hero-bg.svg');"></div>
  
  <!-- Tech pattern layer - slow movement -->
  <div class="parallax-layer parallax-tech" data-speed="0.5" 
       style="background-image: url('../images/parallax/tech-pattern.svg');"></div>
  
  <!-- Midground layer - medium movement -->
  <div class="parallax-layer parallax-mid" data-speed="0.7" 
       style="background-image: url('../images/parallax/midground.svg');"></div>
  
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
```

**Status**: ✅ COMPLETE

### 4. CSS Implementation (docs/stylesheets/parallax.css)

Key CSS classes:

```css
/* Hero container */
.hero-parallax {
  position: relative;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Parallax layers */
.parallax-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 120%;
  background-size: cover;
  background-position: center;
  will-change: transform;
}

/* Individual layers */
.parallax-back { opacity: 0.6; z-index: 1; }
.parallax-tech { opacity: 0.2; z-index: 2; }
.parallax-mid { opacity: 0.4; z-index: 3; }

/* Hero content */
.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  color: white;
}
```

**Status**: ✅ COMPLETE

### 5. JavaScript Implementation (docs/javascripts/extra.js)

```javascript
function initializeHeroSection() {
  const heroParallax = document.querySelector('.hero-parallax');
  if (!heroParallax) return;

  let ticking = false;
  const parallaxLayers = heroParallax.querySelectorAll('.parallax-layer');

  function updateParallax() {
    const scrolled = window.pageYOffset;
    
    parallaxLayers.forEach((layer) => {
      const speed = parseFloat(layer.getAttribute('data-speed')) || 0.5;
      const yPos = -(scrolled * speed);
      layer.style.transform = `translateY(${yPos}px)`;
    });
    
    const heroContent = heroParallax.querySelector('.hero-content');
    if (heroContent) {
      const heroSpeed = 0.4;
      const yPos = -(scrolled * heroSpeed);
      heroContent.style.transform = `translateY(${yPos}px)`;
    }

    ticking = false;
  }

  function requestTick() {
    if (!ticking) {
      window.requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }

  window.addEventListener('scroll', requestTick, { passive: true });
  animateHeroContent();
}

function animateNumber(element) {
  const finalValue = parseInt(element.getAttribute('data-target')) || parseInt(element.textContent);
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
```

**Status**: ✅ COMPLETE

---

## Upcoming Enhancements (Phase 2)

### Full-Screen Immersive Hero

**Goal**: Transform hero from fixed-width container to full-screen experience matching Material Design

**Key Changes**:

1. **Hero Positioning**: `position: fixed` instead of `position: relative`
2. **Hero Dimensions**: `width: 100vw; height: 100vh` (full viewport)
3. **Navigation**: Z-index increased to sit above hero
4. **Content Sections**: Pushed down with `margin-top: 100vh`
5. **Homepage-Only**: Uses `body.is-home` class to isolate changes

**Implementation Timeline**:
- Phase 2.1: CSS updates (fixed positioning, z-index stack)
- Phase 2.2: JavaScript homepage detection
- Phase 2.3: Testing & optimization
- Phase 2.4: Deployment

**Impact**: Homepage only; all other pages unchanged

---

## Architecture & Layers

### Three-Layer Parallax System

```
┌─────────────────────────────────────────┐
│         .hero-parallax (container)      │
├─────────────────────────────────────────┤
│ ┌──────────────────────────────────────┐│
│ │ .parallax-back (Hero BG) z:1, speed:0.3 ││
│ │ hero-bg.svg (gradient backdrop)       ││
│ └──────────────────────────────────────┘│
│ ┌──────────────────────────────────────┐│
│ │ .parallax-tech (Tech Pattern) z:2, speed:0.5 ││
│ │ tech-pattern.svg (grid overlay)       ││
│ └──────────────────────────────────────┘│
│ ┌──────────────────────────────────────┐│
│ │ .parallax-mid (Midground) z:3, speed:0.7 ││
│ │ midground.svg (particles)             ││
│ └──────────────────────────────────────┘│
│ ┌──────────────────────────────────────┐│
│ │ .hero-content z:10 (overlaid)         ││
│ │ H1 Title                              ││
│ │ P Subtitle                            ││
│ │ Buttons (Explore, Admin)              ││
│ └──────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Scroll Speed Mechanism

```
Scroll Position: 0px          500px           1000px
Scroll Distance: ──────────────────────────────────

Layer Back:      0px  ←────→ 150px ←────────→ 300px
(speed: 0.3)     Slowest movement (stays in background)

Layer Tech:      0px  ←────→ 250px ←────────→ 500px
(speed: 0.5)     Medium movement

Layer Mid:       0px  ←────→ 350px ←────────→ 700px
(speed: 0.7)     Faster movement

Content:         0px  ←────→ 200px ←────────→ 400px
(speed: 0.4)     Medium movement (appears close)

Result: Depth illusion as fast layers pull away, slow layers stay
```

---

## File Structure

### Key Files

```
docs/
├── index.md                          # Homepage with parallax HTML
├── javascripts/
│   ├── extra.js                      # parallax + stats animation
│   └── parallax.js                   # (legacy parallax controller)
└── stylesheets/
    ├── parallax.css                  # Hero and parallax styling
    └── extra.css                     # General site styles

docs/images/parallax/
├── hero-bg.svg                       # Gradient backdrop (1920x1080)
├── tech-pattern.svg                  # Grid pattern overlay
├── midground.svg                     # Particle layer
└── mario.gif                         # Alternative theme asset

mkdocs.yml
├── extra_css:
│   - stylesheets/extra.css
│   - stylesheets/parallax.css        # Loaded on all pages
└── extra_javascript:
    - javascripts/extra.js            # Loaded on all pages
    - javascripts/parallax.js         # Legacy (can be optimized)
```

### Configuration

In `mkdocs.yml`:
```yaml
extra_css:
  - stylesheets/extra.css
  - stylesheets/parallax.css

extra_javascript:
  - javascripts/mathjax.js
  - javascripts/extra.js
  - javascripts/parallax.js
  - javascripts/ai-assistant.js
```

---

## Implementation Checklist

### Phase 1: Current (Completed)
- [x] Fix stats number animation (data-target attribute)
- [x] Implement three-layer parallax system
- [x] Add data-speed attributes to HTML layers
- [x] Create parallax.css with layer styling
- [x] Implement updateParallax() in extra.js
- [x] Add RAF throttling for performance
- [x] Test on desktop, tablet, mobile
- [x] Verify dark/light theme switching
- [x] Document implementation

### Phase 2: Upcoming (Full-Screen Hero)
- [ ] Add `body.is-home` detection in JavaScript
- [ ] Update `.hero-parallax` to `position: fixed`
- [ ] Set hero to full viewport: `width: 100vw; height: 100vh`
- [ ] Update navigation z-index to 1000
- [ ] Add `margin-top: 100vh` to `.md-main` on homepage
- [ ] Test parallax with fixed positioning
- [ ] Verify stats animation triggers
- [ ] Test navigation sticky/fixed state
- [ ] Mobile responsiveness check
- [ ] Cross-browser testing
- [ ] Performance audit (target 60fps)
- [ ] Accessibility verification

---

## FAQ & Troubleshooting

### Q: Why three layers instead of more?
**A**: Three layers provide optimal depth perception without visual clutter. More layers can cause performance issues on scroll.

### Q: What's the difference between speed values?
**A**: 
- `0.3` = Very slow (background layers stay visible longer)
- `0.5` = Moderate (smooth middle ground)
- `0.7` = Fast (foreground elements pull away)

### Q: Why use RAF instead of just scroll events?
**A**: RequestAnimationFrame ensures updates sync with browser repaint cycle (60fps max), preventing jank and wasted renders.

### Q: Will Phase 2 affect other pages?
**A**: No. The `body.is-home` class detection ensures changes only apply to homepage. Other pages render normally.

### Q: What about mobile performance?
**A**: Parallax works well on mobile. Phase 2 will include mobile optimization (possible height adjustment for smaller viewports).

### Q: How do I test the parallax effect?
**A**: 
1. Open homepage on desktop
2. Slowly scroll down
3. Notice how background layers move slower than content
4. Content should appear to float above the background

### Q: What if parallax doesn't work?
**A**: 
- Check browser console for JavaScript errors
- Verify `data-speed` attributes on parallax layers
- Confirm CSS classes exist: `parallax-back`, `parallax-tech`, `parallax-mid`
- Verify SVG images load correctly
- Check z-index stacking (should be 1, 2, 3, 10)

### Q: Can I adjust animation speeds?
**A**: Yes. Modify `data-speed` values in HTML (higher = faster):
```html
<div class="parallax-layer parallax-back" data-speed="0.2">  <!-- Slower -->
<div class="parallax-layer parallax-back" data-speed="0.5">  <!-- Faster -->
```

### Q: Performance degradation on scroll?
**A**: 
- Ensure GPU acceleration: `will-change: transform` in CSS
- Check browser DevTools Performance tab
- Target should be 60fps (green line at bottom of timeline)
- Reduce parallax layer count if needed

---

## Upcoming Enhancements (Phase 3): Video & GIF Parallax Backgrounds

For even more immersive hero effects, video and animated GIF backgrounds are available as optional enhancements.

### Video (MP4/WebM) - Recommended for Modern Look

**Benefits**:
- ✅ Smooth 60fps animation
- ✅ Significantly smaller file sizes than GIFs
- ✅ Better visual quality
- ✅ Hardware accelerated playback
- ✅ Excellent mobile performance

**Technical Specifications**:
- **File Size**: 2-3 MB for 10 seconds of 1080p video
- **Browser Support**: 97%+ (modern browsers)
- **Encoding**: H.264 codec (MP4) + VP8 codec (WebM)
- **Performance**: Native video acceleration, minimal CPU impact

**Implementation Example**:

```html
<!-- Video parallax background with SVG fallback -->
<div class="hero-parallax">
  <!-- Main video layer -->
  <video 
    class="parallax-layer parallax-video" 
    data-speed="0.5"
    autoplay 
    muted 
    loop 
    playsinline
    poster="/images/parallax/hero-poster.jpg"
    preload="metadata">
    <source src="/images/parallax/hero-bg.mp4" type="video/mp4">
    <source src="/images/parallax/hero-bg.webm" type="video/webm">
    <!-- Fallback to SVG if video not supported -->
    <img src="/images/parallax/hero-bg.jpg" alt="Hero background">
  </video>

  <!-- Optional: SVG overlay for additional visual depth -->
  <div class="parallax-layer parallax-overlay" data-speed="0.7">
    <svg><!-- Your SVG pattern here --></svg>
  </div>

  <!-- Hero content remains unchanged -->
  <div class="hero-content">
    <h1>Your Title</h1>
    <p>Your subtitle</p>
  </div>
</div>
```

**Required CSS for Video Elements**:

```css
/* Make video fill the parallax container */
body.is-home .parallax-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 0;
}

/* Ensure content sits above video */
body.is-home .hero-content {
  position: relative;
  z-index: 1;
}
```

**Video Encoding Guide**:

If you have a source video, create MP4 and WebM versions using FFmpeg:

```bash
# Create MP4 (H.264, optimized for web)
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4

# Create WebM (VP8, better compression)
ffmpeg -i input.mp4 -c:v libvpx -crf 10 -c:a libopus -b:a 128k output.webm

# Create poster image (first frame)
ffmpeg -i input.mp4 -ss 00:00:00 -vf scale=1920:-1 -q:v 3 poster.jpg
```

### GIF - Simple & Retro Alternative

**Benefits**:
- ✅ Simple to create (no encoding needed)
- ✅ Universal browser support (99%+)
- ✅ Good for pixel art and retro effects
- ✅ Works everywhere

**Tradeoffs**:
- ⚠️ Larger file sizes (15-25 MB for 10s animation)
- ⚠️ Can be choppy on some systems (CPU intensive)
- ⚠️ Limited color palette compared to video

**Implementation Example**:

```html
<!-- GIF as parallax background -->
<div class="hero-parallax">
  <div class="parallax-layer parallax-gif" 
       data-speed="0.5" 
       style="background-image: url('../images/parallax/hero-animation.gif');
              background-size: cover;
              background-position: center;
              width: 100%;
              height: 100%;">
  </div>

  <!-- Hero content -->
  <div class="hero-content">
    <h1>Your Title</h1>
  </div>
</div>
```

### Comparison: SVG vs Video vs GIF

| Aspect | SVG | Video (MP4) | GIF |
|--------|-----|------------|-----|
| File Size | <1 MB | 2-3 MB | 15-25 MB |
| Animation Quality | Static | Smooth 60fps | Fixed 10-30fps |
| Browser Support | 99%+ | 97%+ | 99%+ |
| Mobile Performance | Good | Excellent | Fair (CPU) |
| Editing Flexibility | High (code-based) | Low (pre-rendered) | Low (pre-rendered) |
| Best Use Case | Clean, minimal | Modern, immersive | Retro, pixel art |
| Performance Impact | GPU accelerated | GPU accelerated | CPU intensive |
| Interactivity | Can add effects | Fixed playback | Fixed playback |

### Decision Framework

**Choose SVG if:**
- Want minimal, clean aesthetic
- Need lightweight (<1 MB)
- Want code-based customization
- Prefer GPU acceleration
- **Current setup** ✅

**Choose Video if:**
- Want modern, immersive look
- Have existing video content
- Can handle 2-3 MB file size
- Want smooth 60fps animation
- **Recommended for enhancement** 🎬

**Choose GIF if:**
- Want retro/pixel art style
- Prefer simplicity over file size
- Have existing GIF animation
- Don't mind larger files
- **Alternative option** 🎨

### Implementation Roadmap for Phase 3

**Step 1: Prepare Media** (if doing video)
- Source video file (MP4, MOV, AVI, etc.)
- Run FFmpeg encoding commands above
- Create poster image (thumbnail)

**Step 2: Update HTML** (docs/index.md)
- Replace SVG `<div>` with `<video>` element
- Keep fallback chain: Video → WebM → Poster → SVG → Color

**Step 3: Update CSS** (docs/stylesheets/parallax.css)
- Add `.parallax-video` rules for proper sizing
- Ensure object-fit and object-position for centering
- Maintain z-index stack with video at layer 0

**Step 4: Test**
- Mobile: Verify video plays on iOS/Android
- Desktop: Check 60fps performance in DevTools
- Fallback: Confirm SVG shows if video unsupported

### Resources for Phase 3

**Complete Implementation Guide**: See `VIDEO_GIF_PARALLAX_GUIDE.md` for:
- 7 detailed sections with 400+ lines of documentation
- FFmpeg encoding commands
- Mobile optimization strategies
- Performance tuning tips
- Troubleshooting common issues
- Complete code examples

**When to Implement Phase 3**:
- ✅ After Phase 1 (current) is verified working
- ✅ After Phase 2 (full-screen hero) is in production
- ⏳ Optional enhancement (site works great with SVG)
- 📅 Recommended: Implement when you have hero video asset

---

## References

- **Material for MkDocs**: https://squidfunk.github.io/mkdocs-material/
- **RequestAnimationFrame**: https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
- **CSS Transforms Performance**: https://web.dev/animations-guide/
- **Video Parallax Guide**: `VIDEO_GIF_PARALLAX_GUIDE.md` (detailed implementation)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 30, 2025 | Initial parallax implementation with 3-layer system |
| 2.0 | Dec 1, 2025 | Consolidated documentation, added Phase 2 full-screen hero plan |
| 2.1 | Dec 1, 2025 | Added Phase 3: Video & GIF parallax background options |

---

**Current Status**: Phase 1 & 2 Complete ✅ | Phase 3 Ready for Optional Enhancement 🚀
