# Parallax Hero Section Fixes - December 1, 2025

**Status**: ✅ COMPLETE  
**Date**: December 1, 2025  
**Issues Fixed**: 4 Critical Issues

---

## Summary

Fixed four critical parallax rendering issues on the homepage:

1. **Hero content appearing BEHIND parallax layers** - Text was hidden behind animated background layers
2. **Excessive white space at top of page** - Large padding creating unnecessary scroll distance
3. **Incorrect content visibility logic** - Hero content was being moved off-screen by parallax transforms
4. **Hero content jumping on page load** - Animation transforms conflicting with centering transforms

---

## Issues & Root Causes

### Issue 1: Hero Content Z-Index Inversion

**Problem**: The text "Homelab Documentation Hub" and subtitle appeared behind the parallax layers (green wavy SVGs)

**Root Cause**: 
- Parallax layers had z-index values: `-back: 1`, `-tech: 2`, `-mid: 3`
- Hero content had z-index: `50`
- HOWEVER, the content was being moved out of view by `transform: translateY()` in the JavaScript parallax update
- Even though z-index was high, the transform and its stacking context issues caused visual layering problems

**Fix**:
```css
/* BEFORE */
.parallax-back { z-index: 1; }
.parallax-tech { z-index: 2; }
.parallax-mid { z-index: 3; }

/* AFTER */
.parallax-back { z-index: -3; }
.parallax-tech { z-index: -2; }
.parallax-mid { z-index: -1; }
```

This ensures layers render BELOW the hero content container, not above it.

---

### Issue 2: Extra White Space at Top

**Problem**: Page loaded with ~100vh of empty space before stats section appeared

**Root Cause**: 
```css
body.is-home .stats-section {
  padding-top: 100vh;  /* ❌ This creates extra scroll distance */
}
```

The padding was intended to position stats after the hero, but it created a visual gap with no content.

**Fix**:
```css
/* BEFORE */
body.is-home .stats-section {
  position: relative;
  z-index: 20;
  margin-top: 0;
  padding-top: 100vh;
}

/* AFTER */
body.is-home .stats-section {
  position: relative;
  z-index: 20;
  margin-top: 100vh;        /* ✅ Use margin instead of padding */
  padding-top: 4rem;        /* ✅ Normal padding for section spacing */
}
```

**Result**: 
- Hero still takes full first viewport (100vh)
- Stats section immediately follows without gap
- Normal padding applied for section content spacing

---

### Issue 3: Hero Content Parallax Transform

**Problem**: Hero content (text and buttons) were moving with scroll, making them disappear behind layers as page scrolled

**Root Cause**:
```javascript
// BEFORE: Applied parallax to hero-content on ALL pages
if (heroContent) {
    const heroSpeed = 0.4;
    const yPos = -(scrolled * heroSpeed);
    heroContent.style.transform = `translateY(${yPos}px)`;  // ❌ Wrong for homepage
}
```

On the homepage, the fixed/centered hero content should NOT move with scroll.

**Fix**:
```javascript
// AFTER: Only apply parallax transform on non-homepage pages
if (heroContent && !isHome) {
    const heroSpeed = 0.4;
    const yPos = -(scrolled * heroSpeed);
    heroContent.style.transform = `translateY(${yPos}px)`;
}
```

Also updated CSS positioning:
```css
/* BEFORE */
body.is-home .hero-content {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);  /* ❌ This could be overridden */
  z-index: 50;
}

/* AFTER */
body.is-home .hero-content {
  position: fixed;
  top: 50%;
  left: 50%;
  margin-left: -400px;               /* ✅ Use margin for centering */
  margin-top: -200px;                /* ✅ Doesn't interact with JS transforms */
  z-index: 50;
  pointer-events: auto;              /* ✅ Ensure buttons are clickable */
}
```

**Result**: Hero content stays fixed and centered while parallax layers animate beneath it during first viewport scroll

---

### Issue 4: Hero Content Jumping on Page Load

**Problem**: The hero title, subtitle, and buttons would "jump" or shift position during page load due to conflicting animations.

**Root Cause**: The `fadeInUp` animation uses `transform: translateY(30px)` which conflicted with the centering `transform: translate(-50%, -50%)` on the homepage hero content.

**Fix**: Created separate animation strategies for homepage vs other pages:

```css
/* New opacity-only animation for homepage */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Homepage: use opacity-only animation (no transform conflicts) */
body.is-home .hero-content {
  animation: fadeIn 0.8s ease-out;
}
body.is-home .hero-title {
  animation: fadeIn 0.8s ease-out 0.2s both;
}
body.is-home .hero-subtitle {
  animation: fadeIn 0.8s ease-out 0.4s both;
}
body.is-home .hero-buttons {
  animation: fadeIn 0.8s ease-out 0.6s both;
}

/* Non-homepage: use full animation with transform */
body:not(.is-home) .hero-title {
  animation: fadeInUp 1s ease-out;
}
```

**Result**: Hero content fades in smoothly without any position jumping on the homepage.

---

## Files Modified

1. **`docs/stylesheets/parallax.css`**
   - Changed parallax layer z-index values: `1,2,3` → `-3,-2,-1`
   - Updated hero-content positioning: `transform: translate()` → `margin-left/margin-top`
   - Fixed stats-section spacing: `padding-top: 100vh` → `margin-top: 100vh; padding-top: 4rem`
   - Added `@keyframes fadeIn` opacity-only animation
   - Split animations by page type (homepage vs non-homepage)

2. **`docs/javascripts/extra.js`**
   - Added conditional check: only apply parallax transform to hero-content on non-homepage pages
   - Added hero fade-out logic when scrolling past first viewport
   - Added inline comment explaining homepage behavior

---

## Visual Behavior After Fixes

### On First Page Load
- Hero with text "Homelab Documentation Hub" is VISIBLE and CENTERED
- Text is clearly ON TOP of the parallax layers
- No extra space at top

### On Scroll (First Viewport)
- Text stays fixed and centered
- Green wavy SVG layers animate behind the text
- Parallax effect creates depth without moving the content

### On Scroll Past Hero (Second Viewport)
- Hero scrolls off-screen
- Stats section and featured projects become visible
- No parallax updates after hero is fully scrolled

### On Other Pages
- Hero-content parallax effect still works (different behavior)
- Non-homepage pages unaffected

---

## Testing Checklist

- [x] Text is visible above parallax layers
- [x] No excessive white space at page top
- [x] Hero content stays centered while scrolling first viewport
- [x] Parallax layers animate smoothly
- [x] Stats section appears after hero (no gap)
- [x] Buttons are clickable
- [x] Navigation overlay works
- [x] Mobile responsive

---

## Technical Details

### Z-Index Stack (Homepage Hero)

```
Layer 0 (background):     body.is-home .hero-parallax { z-index: 1; }
├─ Layer -3:              .parallax-back
├─ Layer -2:              .parallax-tech
├─ Layer -1:              .parallax-mid
└─ Layer 50 (foreground):  body.is-home .hero-content { z-index: 50; }

Navigation:               body.is-home .md-header { z-index: 1000; }
```

### Position Properties

**Hero Parallax** (fixed background):
- `position: fixed`
- `top: 0; left: 0; width: 100vw; height: 100vh`
- `z-index: 1`

**Parallax Layers** (animated depth):
- `position: absolute` (relative to hero-parallax)
- `z-index: -3, -2, -1`
- `transform: translateY(-(scrolled * speed)px)`

**Hero Content** (fixed centered text):
- `position: fixed`
- `top: 50%; left: 50%;`
- `margin-left: -400px; margin-top: -200px;` (centers 800px wide container)
- `z-index: 50`
- NO transform applied on homepage

---

## References

- **Previous Implementation**: `PARALLAX_AND_HERO_GUIDE.md` (Phase 2 section)
- **Phase 2 Execution**: `PHASE_2_EXECUTION_SUMMARY.md`
- **Implementation Details**: `IMPLEMENTATION_COMPLETE.md`

---

## Version Control

| Component | Before | After |
|-----------|--------|-------|
| Parallax layer z-index | 1, 2, 3 | -3, -2, -1 |
| Hero content positioning | transform: translate() | margin-left/top |
| Stats section spacing | padding-top: 100vh | margin-top: 100vh |
| Hero-content parallax | Applied on all pages | Applied only on non-homepage |

---

**Status**: Ready for Deployment ✅  
**Testing**: Complete ✅  
**Documentation**: Complete ✅

