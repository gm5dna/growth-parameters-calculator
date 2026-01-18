# Future Improvements Backlog

This document tracks potential enhancements for the Growth Parameters Calculator. Features are categorized by type and priority.

## Completed Features ✅

1. ~~Dark mode theme with system preference detection~~
2. ~~Copy results to clipboard button~~
3. ~~Export to PDF/CSV/print-friendly view~~ (PDF export completed)

---

## User Experience - Quick Wins

2. Keyboard shortcuts (Ctrl+Enter to calculate, Ctrl+R to reset)
3. Undo/redo functionality for form changes
4. **Recent calculations history** (last 5-10 in sidebar)
6. Patient session management (save/switch between patients)
7. Guided tour/onboarding for new users
8. Comparison view (current vs previous visit)
9. Customizable units (imperial/metric toggle)

## Data & Analytics

11. Screenshot/image export for charts
12. **Growth trajectory tracking (multiple measurements over time)**
13. Data import from CSV/EMR systems
14. Statistics dashboard with usage analytics

## Chart Enhancements

15. Chart annotations (add notes to points)
16. **Chart download options (PNG, SVG, PDF)**
17. Growth velocity charts with centiles
18. Multi-patient comparison charts
19. Custom chart ranges with zoom/pan
20. 3D growth charts (height vs weight vs age)

## Clinical Features

21. Bone age integration (Greulich-Pyle/TW3)
22. Puberty staging (Tanner) selector
23. Predicted adult height (Bayley-Pinneau, Khamis-Roche)
24. **BMI categories with WHO classifications**
25. Red flag alerts (growth faltering detection)
26. Syndrome-specific charts (Noonan, Achondroplasia, Prader-Willi)
27. Nutritional calculations (caloric/protein requirements)
28. Lab integration (IGF-1, IGFBP-3, thyroid)

## Accessibility & Localization

29. Screen reader optimization
30. High contrast mode (WCAG AAA)
31. Multi-language support (Spanish, French, Mandarin)
32. Voice input for measurements

## Data Management

33. Offline mode improvements with sync
34. Cloud sync with encryption
35. FHIR API integration
36. Database backend (PostgreSQL)

## Testing & Quality

37. **E2E testing (Cypress/Playwright)**
38. Performance monitoring (RUM, Sentry)
39. A/B testing framework
40. Automated accessibility testing

## Security & Privacy

41. **Privacy mode (no localStorage/ephemeral)**
42. Data encryption for localStorage
43. Audit logging
44. Enhanced rate limiting

## Education & Documentation

45. Contextual help with tooltips
46. Video tutorials
47. FAQ section
48. Interactive examples with sample patients
49. Clinical guidelines integration

## Performance & Technical

50. Code splitting and lazy loading
51. Image optimization (WebP)
52. Service worker improvements
53. GraphQL API
54. WebSocket real-time updates
55. Micro-frontend architecture

---

## Top Priority Items

Based on clinical value and user impact:

1. **#12: Growth trajectory tracking** - Core clinical value
2. **#4: Recent calculations history** - Usability improvement
3. **#16: Chart download options** - Clinical documentation
4. **#24: BMI categories** - Clinical guidance
5. **#2: Keyboard shortcuts** - Power user feature
6. **#41: Privacy mode** - Privacy/compliance
7. **#37: E2E testing** - Code quality

## Implementation Notes

- Features marked in **bold** are considered highest priority
- Completed features are marked with ~~strikethrough~~ and ✅
- For detailed implementation plans, create a new document in `docs/feature-plans/`
- Reference this document when planning sprints or releases
