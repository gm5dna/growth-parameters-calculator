# TODO List - Growth Parameters Calculator

**Last Updated:** 2026-01-18

---

## Known Issues 🐛

### iOS Safari Date Input Alignment
**Priority:** Low
**Status:** Investigated, CSS fixes attempted
**Description:** Date input fields display centered text on iOS Safari instead of left-aligned. This appears to be an iOS Safari quirk that's difficult to override with CSS alone.

**Attempted Fixes:**
- ✗ `text-align: left`
- ✗ Webkit-specific pseudo-element selectors
- ✗ `appearance: none` with aggressive margin/padding overrides
- ✗ `direction: ltr` and `unicode-bidi`

**Next Steps/Options:**
1. Accept iOS default behavior (easiest)
2. JavaScript detection → convert to text input with validation (moderate effort)
3. Custom date picker library like flatpickr (higher effort, more control)

**Impact:** Cosmetic only - functionality not affected

---

## Feature Backlog 📋

See `documentation/feature-plans/FEATURES_BACKLOG.md` for comprehensive list.

### Immediate Priority
- [ ] CDC Reference Support (enable in backend)
- [ ] Weight Target Calculator (weight for target BMI centile)
- [ ] Centile Band Interpretation (e.g., "between 25th-50th centile")

### Short Term
- [ ] Bone Age Assessment
- [ ] Event Annotations (tag measurements with clinical events)
- [ ] Library Age Functions (use rcpchgrowth built-in age calculations)

### Medium Term
- [ ] Serial Measurements & Trajectory Tracking
- [ ] Expected Height from MPH comparison
- [ ] Thrive Lines (experimental)

---

## Enhancements 💡

### Mobile UX Improvements
- [ ] Better haptic feedback on calculate button
- [ ] Pull-to-refresh for results
- [ ] Offline calculation caching

### Chart Improvements
- [ ] Download chart as PNG/SVG
- [ ] Print-optimized chart layout
- [ ] Touch gestures (pinch-to-zoom on chart)

### Clinical Features
- [ ] Recent calculations history (localStorage)
- [ ] Export history to CSV
- [ ] Keyboard shortcuts (Ctrl+Enter to calculate)
- [ ] Voice input for measurements

---

## Documentation 📚

- [ ] Add video tutorial/demo
- [ ] Clinical interpretation guide
- [ ] FAQs section
- [ ] Add examples for each growth reference

---

## Technical Debt 🔧

### Code Quality
- [ ] Add more unit tests for edge cases
- [ ] Increase test coverage for utils.py and models.py
- [ ] Refactor chart generation code (script.js is getting large)
- [ ] Add JSDoc comments to JavaScript functions

### Performance
- [ ] Lazy load Chart.js library
- [ ] Optimize chart rendering for large age ranges
- [ ] Add service worker caching strategy

### Accessibility
- [ ] Full WCAG 2.1 AA compliance audit
- [ ] Screen reader testing
- [ ] Keyboard navigation improvements
- [ ] High contrast mode support

---

## Deployment 🚀

### Current Issues
- [x] Python 3.14 greenlet compatibility (fixed with runtime.txt)
- [x] Material Design icons for dark mode toggle (completed)
- [x] Percentage median BMI feature (completed)
- [x] Mobile rendering issues (completed)

### Future Considerations
- [ ] Set up staging environment
- [ ] Automated deployment testing
- [ ] Performance monitoring (response times, error rates)
- [ ] User analytics (privacy-respecting)

---

## Notes

- Keep production dependencies minimal (requirements.txt)
- Testing dependencies in requirements-dev.txt only
- All new features must include tests
- Maintain CLAUDE.md with completed features
