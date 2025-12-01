# Video & GIF Parallax Backgrounds - Implementation Guide

**Last Updated**: December 1, 2025  
**Status**: Research Complete - Ready for Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Video Background Implementation](#video-background-implementation)
3. [GIF Background Implementation](#gif-background-implementation)
4. [Performance Optimization](#performance-optimization)
5. [Browser Compatibility](#browser-compatibility)
6. [Mobile Considerations](#mobile-considerations)
7. [Code Examples](#code-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What We Can Do

Using **video** (.mp4) or **animated GIF** files as parallax backgrounds creates stunning immersive effects with:

- **Smooth, continuous motion** (video advantage: true continuous animation)
- **Reduced file size** (video advantage: 50-80% smaller than GIFs for same duration)
- **Progressive playback** (video loads frame-by-frame)
- **Better control** (video: play, pause, speed; GIF: fixed animation)

### Current Implementation

Your homepage currently uses **three SVG image layers** with data-speed attributes (0.3, 0.5, 0.7) for parallax depth.

### Adding Video/GIF as Replacement or Enhancement

#### Option A: Replace SVG with Video
- **Pro**: More dynamic, smoother animation, smaller file sizes
- **Con**: Requires encoding, more browser processing
- **Best For**: Hero background takeover effect

#### Option B: Replace SVG with GIF
- **Pro**: Simple, no encoding needed, good browser support
- **Con**: Larger files, fixed animation speed, fewer control options
- **Best For**: Simpler background effects, retro/pixel art styles

#### Option C: Keep SVG, Add Video Overlay
- **Pro**: Maintains fallback with SVG + dynamic video on top
- **Con**: More complex layering, potential performance impact
- **Best For**: Progressive enhancement approach

---

## Video Background Implementation

### Why Video?

**Video (.mp4, .webm) is superior to GIF for parallax backgrounds:**

| Aspect | Video | GIF |
|--------|-------|-----|
| File Size (10s 1080p) | ~2-3 MB | ~15-25 MB |
| Encoding Control | Codec selection (H.264, VP8) | Fixed format |
| Playback Control | ✅ Play/pause/speed | ❌ Auto-loop only |
| Quality at 60fps | ✅ Excellent | ❌ Limited |
| Browser Support | ✅ 97%+ | ✅ 99%+ |
| Mobile Performance | ✅ Hardware accelerated | ⚠️ CPU intensive |
| Parallax Efficiency | ✅ Smooth 60fps | ⚠️ Often choppy |

### HTML Structure

```html
<!-- Video parallax background -->
<div class="hero-parallax">
  <!-- Video layer -->
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
    <!-- Fallback to static image -->
    <img src="/images/parallax/hero-bg.jpg" alt="Hero background">
  </video>

  <!-- Optional: SVG layer on top for visual enhancement -->
  <div class="parallax-layer parallax-overlay" data-speed="0.7">
    <!-- SVG overlay or pattern -->
  </div>

  <!-- Hero content -->
  <div class="hero-content">
    <h1>Your Title Here</h1>
    <p>Subtitle or description</p>
  </div>
</div>
```

### CSS Styling for Video

```css
/* Video parallax layer */
body.is-home .parallax-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 1;
  
  /* Hardware acceleration */
  will-change: transform;
  backface-visibility: hidden;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  body.is-home .parallax-video {
    /* On mobile, reduce video processing for performance */
    filter: brightness(0.9);
    transform: scale(1.1);
  }
}

/* Dark overlay for text readability */
body.is-home .parallax-video::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  z-index: 2;
  pointer-events: none;
}
```

### JavaScript Enhancement for Video Parallax

```javascript
let videoElement = null;
let isVideoPlaying = true;

function initializeVideoParallax() {
  videoElement = document.querySelector('.parallax-video');
  
  if (!videoElement) return;
  
  // Pause video when scrolled past hero
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroHeight = window.innerHeight;
    
    if (scrolled > heroHeight && isVideoPlaying) {
      videoElement.pause();
      isVideoPlaying = false;
    } else if (scrolled <= heroHeight && !isVideoPlaying) {
      videoElement.play();
      isVideoPlaying = true;
    }
  }, { passive: true });
  
  // Handle mobile - reduce playback quality for performance
  if (window.innerWidth < 768) {
    videoElement.playbackRate = 0.8; // Slightly slower on mobile
  }
}

// Fallback for browsers that don't support video autoplay with sound off
document.addEventListener('DOMContentLoaded', () => {
  initializeVideoParallax();
});
```

### Video File Preparation

#### Recording/Creating Video

```bash
# Using FFmpeg to convert video for web
# Create H.264 MP4 (best browser support)
ffmpeg -i video.mov \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -c:a aac \
  -b:a 128k \
  output.mp4

# Create WebM format (better compression)
ffmpeg -i video.mov \
  -c:v libvpx-vp9 \
  -crf 30 \
  -b:v 0 \
  -c:a libopus \
  -b:a 128k \
  output.webm
```

#### Resolution Guidelines

- **Desktop (1920px+)**: 1920x1080 @ 30fps
- **Tablet (768px)**: 1280x720 @ 24fps
- **Mobile (375px)**: 800x450 @ 24fps (optional, consider static image)

#### Target File Sizes

- 10-second loop @ 1080p: 2-3 MB (MP4), 1.5-2 MB (WebM)
- 15-second loop @ 720p: 3-4 MB (MP4), 2-3 MB (WebM)

#### Recommended Encoding Settings

```json
{
  "video_codec": "libx264 or libvpx-vp9",
  "bitrate": "1500-2500k",
  "fps": 24,
  "resolution": "1920x1080",
  "crf": 23,
  "audio": "aac or libopus",
  "audio_bitrate": "128k",
  "file_format": "mp4 with webm fallback"
}
```

---

## GIF Background Implementation

### When to Use GIF

GIFs are good for:
- Simple looping animations (< 5 seconds)
- Retro/pixel art styles
- Maximum browser compatibility
- No encoding tools needed

### GIF Creation

#### Using ImageMagick

```bash
# Convert sequence of PNG frames to GIF
convert -delay 10 -loop 0 frame-*.png animation.gif

# Optimize GIF for web (reduce colors)
convert animation.gif -fuzz 20% -colors 256 optimized.gif

# Resize during conversion
convert -resize 1920x1080 -delay 10 -loop 0 frame-*.png final.gif
```

#### Using FFmpeg

```bash
# Create GIF from video
ffmpeg -i video.mp4 \
  -fps 15 \
  -vf "scale=1920:-1:flags=lanczos" \
  output.gif

# Optimize further
gifsicle -i output.gif -O2 -o optimized.gif
```

### HTML Structure for GIF

```html
<div class="hero-parallax">
  <img 
    class="parallax-layer parallax-gif" 
    data-speed="0.5"
    src="/images/parallax/hero-animation.gif" 
    alt="Animated hero background"
    decoding="async">
  
  <div class="hero-content">
    <!-- Content here -->
  </div>
</div>
```

### CSS for GIF Layer

```css
body.is-home .parallax-gif {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 1;
  
  /* Lazy load GIF to improve initial page speed */
  loading: lazy;
}

/* Reduce GIF processing on mobile */
@media (max-width: 768px) {
  body.is-home .parallax-gif {
    /* Use static fallback image on slow connections */
    @supports (background-image: url(...)) {
      content: url('/images/parallax/hero-static.jpg');
    }
  }
}
```

---

## Performance Optimization

### Video Optimization Checklist

- ✅ Use VP9/WebM for compression (save 30-40%)
- ✅ Limit video to viewport size (don't overencode)
- ✅ Use `preload="metadata"` to defer video load
- ✅ Add `poster` attribute for loading state
- ✅ Pause video when off-screen (save CPU/battery)
- ✅ Use `playsinline` for mobile
- ✅ Provide static image fallback

### GIF Optimization Checklist

- ✅ Limit animation length to 5-10 seconds maximum
- ✅ Reduce frame count (target 30-50 frames)
- ✅ Lower FPS to 12-15 fps
- ✅ Use imagemagick/gifsicle optimization
- ✅ Provide static JPG fallback on slow networks
- ✅ Lazy load with `loading="lazy"` attribute

### Parallax Performance with Video/GIF

```javascript
// Optimize parallax calculations for video background
function updateVideoParallax() {
  const scrolled = window.pageYOffset;
  
  // Only update if hero is visible
  if (scrolled > window.innerHeight * 1.2) {
    return; // Stop calculations when past hero
  }
  
  const video = document.querySelector('.parallax-video');
  if (!video) return;
  
  // Apply transform with will-change hint
  const offset = scrolled * 0.5; // data-speed value
  video.style.transform = `translateY(${offset}px)`;
  
  // Use requestAnimationFrame for smooth 60fps
  video.style.willChange = 'transform';
}

// Throttle with RAF
let rafId = null;
window.addEventListener('scroll', () => {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(updateVideoParallax);
}, { passive: true });
```

### Responsive Image/Video Serving

```html
<!-- Use picture element for responsive video -->
<picture>
  <source media="(min-width: 1920px)" 
          srcset="/images/parallax/hero-1920.mp4 type=video/mp4">
  <source media="(min-width: 1024px)" 
          srcset="/images/parallax/hero-1280.mp4 type=video/mp4">
  <source media="(max-width: 768px)" 
          srcset="/images/parallax/hero-800.mp4 type=video/mp4">
  
  <video autoplay muted loop playsinline>
    <source src="/images/parallax/hero-default.mp4" type="video/mp4">
    <img src="/images/parallax/hero-fallback.jpg" alt="Hero">
  </video>
</picture>
```

---

## Browser Compatibility

### Video Support Matrix

| Browser | MP4 (H.264) | WebM (VP9) | Fallback |
|---------|-----------|----------|----------|
| Chrome 90+ | ✅ | ✅ | N/A |
| Firefox 93+ | ✅ | ✅ | N/A |
| Safari 14+ | ✅ | ❌ | JPG |
| Edge 90+ | ✅ | ✅ | N/A |
| Mobile Safari | ✅ | ❌ | JPG |
| Chrome Mobile | ✅ | ✅ | N/A |

**Recommendation**: Use both MP4 and WebM sources, with JPG fallback

### GIF Support

| Browser | GIF Support | Notes |
|---------|-------------|-------|
| All | ✅ 99%+ | Built-in support |
| Mobile | ✅ | May reduce performance |
| Slow Networks | ⚠️ | Large file sizes |

---

## Mobile Considerations

### Mobile Video Strategy

**Problem**: Videos can drain battery and data on mobile

**Solution**: Progressive Enhancement

```html
<video 
  class="parallax-layer" 
  data-speed="0.5"
  autoplay 
  muted 
  loop 
  playsinline>
  <!-- Desktop: Full quality -->
  <source 
    media="(min-width: 1024px)"
    src="/images/parallax/hero-1080p.mp4" 
    type="video/mp4">
  
  <!-- Mobile: Lower quality -->
  <source 
    media="(max-width: 1024px)"
    src="/images/parallax/hero-480p.mp4" 
    type="video/mp4">
  
  <!-- Fallback -->
  <img src="/images/parallax/hero-static.jpg" alt="Hero">
</video>
```

### Mobile CSS

```css
/* Disable parallax on mobile for performance */
@media (max-width: 768px) {
  body.is-home .parallax-layer {
    /* Use fixed image instead of parallax video */
    background-image: url('/images/parallax/hero-mobile.jpg');
    background-attachment: fixed;
    background-size: cover;
  }
  
  body.is-home .parallax-video {
    display: none; /* Hide video on mobile */
  }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  body.is-home .parallax-layer,
  body.is-home .parallax-video {
    animation: none !important;
    transform: none !important;
  }
}
```

---

## Code Examples

### Complete Hero Section with Video Parallax

```html
<!-- docs/index.md (frontmatter section) -->
<section class="hero-parallax">
  <video 
    class="parallax-layer parallax-video" 
    data-speed="0.5"
    autoplay 
    muted 
    loop 
    playsinline
    poster="/images/parallax/hero-poster.jpg">
    <source src="/images/parallax/hero-bg.mp4" type="video/mp4">
    <source src="/images/parallax/hero-bg.webm" type="video/webm">
    <img src="/images/parallax/hero-poster.jpg" alt="Hero">
  </video>

  <div class="parallax-layer parallax-overlay" data-speed="0.7">
    <svg><!-- Optional overlay pattern --></svg>
  </div>

  <div class="hero-content">
    <h1>Homelab Documentation Hub</h1>
    <p>Professional documentation for your infrastructure</p>
    <div class="hero-buttons">
      <a href="#getting-started" class="md-button md-button--primary">Get Started</a>
      <a href="/admin" class="md-button md-button--secondary">Admin Portal</a>
    </div>
  </div>
</section>

<!-- Stats section (below fold) -->
<div class="stats-section">
  <!-- Stats here -->
</div>
```

### JavaScript Enhancement

```javascript
// docs/javascripts/video-parallax.js
document.addEventListener('DOMContentLoaded', function() {
  const videoElement = document.querySelector('.parallax-video');
  const isHomepage = window.location.pathname === '/';
  
  if (!videoElement || !isHomepage) return;
  
  let isVideoVisible = true;
  
  // Pause video when scrolled past hero
  window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroHeight = window.innerHeight;
    const isVisible = scrolled < heroHeight * 1.5;
    
    if (isVisible && !isVideoVisible) {
      videoElement.play();
      isVideoVisible = true;
    } else if (!isVisible && isVideoVisible) {
      videoElement.pause();
      isVideoVisible = false;
    }
    
    // Apply parallax transform
    if (isVisible) {
      const offset = scrolled * 0.5;
      videoElement.style.transform = `translateY(${offset}px)`;
    }
  }, { passive: true });
  
  // Mobile optimization
  if (window.innerWidth < 768) {
    videoElement.playbackRate = 0.9;
    videoElement.muted = true;
  }
});
```

### CSS Enhancements

```css
/* docs/stylesheets/video-parallax.css */

body.is-home .parallax-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  will-change: transform;
}

body.is-home .parallax-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.3) 100%);
}

body.is-home .hero-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
  text-align: center;
  color: white;
  width: 90%;
  max-width: 600px;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  body.is-home .parallax-video {
    filter: brightness(0.85);
  }
}

@media (max-width: 768px) {
  body.is-home .parallax-video {
    display: none;
  }
  
  body.is-home .hero-parallax {
    background: url('/images/parallax/hero-mobile.jpg') center/cover fixed;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  body.is-home .parallax-video {
    animation: none;
    transform: none !important;
  }
}
```

---

## Troubleshooting

### Video Won't Play

**Problem**: `<video>` tag shows play button but won't autoplay

**Solutions**:
1. Ensure video is **muted** (browsers require this for autoplay)
2. Add `playsinline` attribute (required for iOS)
3. Check video codec support (use both MP4 + WebM)
4. Verify poster image exists

```html
<!-- Correct -->
<video autoplay muted loop playsinline>
  <source src="video.mp4" type="video/mp4">
</video>
```

### Video Performance Issues

**Problem**: Choppy scrolling or high CPU usage

**Solutions**:
1. **Reduce video resolution** on mobile
2. **Lower video bitrate** (target 1500-2500k)
3. **Use WebM format** instead of MP4 (better compression)
4. **Pause video when off-screen** (JavaScript)
5. **Disable parallax on mobile** (use fixed background instead)

### GIF Too Large

**Problem**: GIF file size > 10 MB

**Solutions**:
1. **Reduce frame count**: `gifsicle -i input.gif -o output.gif --optimize=3`
2. **Lower resolution**: `convert input.gif -resize 1280x720 output.gif`
3. **Reduce FPS**: `ffmpeg -i input.gif -vf "fps=10" output.gif`
4. **Increase color reduction**: `convert input.gif -colors 128 output.gif`

### Fallback Image Not Showing

**Problem**: Video fails but fallback doesn't appear

**Solution**: Ensure fallback is inside `<video>` tag

```html
<!-- ❌ Wrong - fallback won't show -->
<video src="video.mp4"></video>
<img src="fallback.jpg">

<!-- ✅ Correct -->
<video>
  <source src="video.mp4">
  <img src="fallback.jpg">
</video>
```

### Mobile Video Not Playing

**Problem**: Video plays on desktop but not mobile

**Solutions**:
1. Add `playsinline` attribute
2. Add `muted` attribute (required for autoplay on mobile)
3. Provide lower quality version for mobile
4. Test on actual mobile device (emulator may not match)

```html
<video 
  autoplay 
  muted 
  loop 
  playsinline>
  <source src="video.mp4" type="video/mp4">
</video>
```

---

## Next Steps

### Recommended Implementation Order

1. **Prepare video files**
   - Record or source hero video (10-15 seconds)
   - Encode to MP4 and WebM
   - Create poster image

2. **Update HTML structure**
   - Replace SVG layers with `<video>` element
   - Add fallback image inside `<video>` tag
   - Keep existing SVG overlay if desired

3. **Add CSS styling**
   - Apply video-specific CSS rules
   - Test responsive breakpoints
   - Verify parallax animation

4. **Enhance with JavaScript**
   - Add pause/play logic based on scroll
   - Optimize for mobile performance
   - Test on various devices

5. **Performance testing**
   - Check video loads quickly
   - Verify parallax smooth (60fps)
   - Test mobile battery impact
   - Measure page load time

### File Organization

```
docs/images/parallax/
├── hero-bg.mp4          # Desktop (1920x1080)
├── hero-bg.webm         # Desktop VP9 format
├── hero-480p.mp4        # Mobile (800x450)
├── hero-poster.jpg      # Loading poster
├── hero-fallback.jpg    # Ultimate fallback
├── hero-mobile.jpg      # Mobile background
├── tech-pattern.svg     # Optional overlay
└── README.md            # Documentation
```

---

## Resources

- **FFmpeg Video Encoding**: https://trac.ffmpeg.org/wiki/Encode/H.264
- **WebM VP9 Codec**: https://developers.google.com/media/vp9/
- **HTML Video Element**: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
- **GIF Optimization**: https://www.lcdf.org/gifsicle/
- **Video Parallax Examples**: https://codepen.io/search/pens?q=video%20parallax

---

**Status**: Ready for Implementation  
**Next**: Coordinate with authentication gateway implementation
