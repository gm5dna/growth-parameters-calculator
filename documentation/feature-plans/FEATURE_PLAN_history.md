# Feature Plan: Recent Calculations History

**Feature ID:** #4
**Priority:** High (Top 5)
**Estimated Effort:** 1-2 days
**Status:** Planning

## Overview

Add a Recent Calculations History feature that stores the last 5-10 calculations in localStorage, allowing users to quickly access and restore previous patient measurements without re-entering data.

## User Stories

1. **As a clinician**, I want to see my recent calculations so I can quickly reference or reload previous patients
2. **As a user**, I want to click on a history entry to restore all form data and results
3. **As a user**, I want to delete individual history entries to manage my privacy
4. **As a user**, I want to clear all history at once
5. **As a power user**, I want history entries to show key identifiers (age, sex, date) for quick scanning

## Requirements

### Functional Requirements
- [x] Store last 10 calculations in localStorage
- [x] Display history in a collapsible sidebar/panel
- [x] Show calculation timestamp, patient sex, age, and key measurements
- [x] Click to restore entire calculation (form data + results)
- [x] Delete individual history entries
- [x] Clear all history button
- [x] Auto-save successful calculations to history
- [x] Prevent duplicate consecutive entries (same data)
- [x] Respect privacy mode (if implemented, don't save history)

### Non-Functional Requirements
- [x] History loads instantly (<100ms)
- [x] Minimal storage footprint (<50KB for 10 entries)
- [x] Mobile-responsive design
- [x] Accessible keyboard navigation
- [x] Works offline (localStorage)

## Design

### Data Structure

```javascript
// localStorage key: 'calculationHistory'
{
  version: 1,  // For future migrations
  maxEntries: 10,
  entries: [
    {
      id: "calc_1705521234567",  // Timestamp-based ID
      timestamp: "2026-01-17T20:53:54.567Z",
      formData: {
        sex: "male",
        birth_date: "2020-01-01",
        measurement_date: "2023-01-01",
        weight: "15",
        height: "90",
        ofc: "",
        // ... all form fields
      },
      results: {
        age: "3.0 years",
        weight_centile: 50,
        height_centile: 25,
        // ... all calculation results
      },
      metadata: {
        sex: "male",
        ageYears: 3.0,
        hasWeight: true,
        hasHeight: true,
        hasOFC: false,
        reference: "uk-who"
      }
    },
    // ... more entries (newest first)
  ]
}
```

### UI Design

#### Option A: Sidebar Panel (Recommended)
```
┌─────────────────────────────────┐
│ [☰] History (3)          [×]    │
├─────────────────────────────────┤
│ 🕐 Today, 2:53 PM               │
│ Male, 3.0y | W:15kg H:90cm      │
│ [Load] [🗑️]                     │
├─────────────────────────────────┤
│ 🕐 Today, 1:20 PM               │
│ Female, 5.5y | W:18kg H:110cm   │
│ [Load] [🗑️]                     │
├─────────────────────────────────┤
│ 🕐 Yesterday, 4:15 PM           │
│ Male, 2.3y | W:12kg H:85cm      │
│ [Load] [🗑️]                     │
├─────────────────────────────────┤
│ [Clear All History]             │
└─────────────────────────────────┘
```

#### Option B: Dropdown Menu
- Dropdown button in header next to mode toggle
- Shows last 5 entries (compact view)
- "See all" link opens full history panel

#### Recommended: Start with **Option A** (more visible, better UX)

### UI Components

1. **History Toggle Button**
   - Location: Top-right header, next to mode toggle
   - Icon: Clock/history icon + badge with count
   - Shows/hides history sidebar

2. **History Sidebar**
   - Slides in from right side
   - Width: 300px desktop, 100% mobile
   - Overlays main content (modal-like)
   - Backdrop click to close

3. **History Entry Card**
   - Timestamp (relative: "2 hours ago", "Yesterday")
   - Patient summary (Sex, Age)
   - Key measurements (W, H, OFC if present)
   - "Load" button (primary action)
   - Delete button (secondary, icon only)
   - Hover state shows full details

4. **Empty State**
   - Icon + message: "No recent calculations yet"
   - Prompt: "Complete a calculation to see it here"

## Implementation Plan

### Phase 1: Data Layer (2-3 hours)
```javascript
// static/history.js

class CalculationHistory {
  constructor(maxEntries = 10) {
    this.storageKey = 'calculationHistory';
    this.maxEntries = maxEntries;
    this.load();
  }

  load() {
    // Load from localStorage
  }

  save() {
    // Save to localStorage with error handling
  }

  add(formData, results) {
    // Add new entry
    // Check for duplicates
    // Trim to maxEntries
    // Save
  }

  get(id) {
    // Retrieve specific entry
  }

  getAll() {
    // Get all entries (newest first)
  }

  delete(id) {
    // Remove specific entry
  }

  clear() {
    // Remove all entries
  }

  isDuplicate(formData) {
    // Check if last entry has same data
  }
}
```

### Phase 2: UI Components (3-4 hours)

**HTML Changes (templates/index.html):**
```html
<!-- History Toggle Button -->
<button id="historyToggle" class="btn-history" aria-label="Show calculation history">
  <span class="icon">🕐</span>
  <span class="badge" id="historyCount">0</span>
</button>

<!-- History Sidebar -->
<div id="historySidebar" class="history-sidebar" role="dialog" aria-labelledby="historyTitle">
  <div class="history-header">
    <h2 id="historyTitle">Recent Calculations</h2>
    <button class="btn-close" aria-label="Close history">&times;</button>
  </div>

  <div id="historyList" class="history-list">
    <!-- Dynamic content -->
  </div>

  <div class="history-footer">
    <button id="clearHistory" class="btn-clear-history">Clear All History</button>
  </div>
</div>

<!-- Backdrop -->
<div id="historyBackdrop" class="history-backdrop"></div>
```

**CSS Additions (static/style.css):**
```css
/* History button in header */
.btn-history {
  position: relative;
  /* Styling */
}

.btn-history .badge {
  /* Count badge */
}

/* Sidebar */
.history-sidebar {
  position: fixed;
  right: -320px;  /* Hidden by default */
  top: 0;
  width: 320px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0,0,0,0.1);
  transition: right 0.3s ease;
  z-index: 1000;
}

.history-sidebar.open {
  right: 0;
}

/* Mobile responsive */
@media (max-width: 600px) {
  .history-sidebar {
    width: 100%;
    right: -100%;
  }
}

/* History entry card */
.history-entry {
  /* Card styling */
}
```

**JavaScript (static/history.js + script.js integration):**
```javascript
// Initialize history
const history = new CalculationHistory();

// Toggle sidebar
document.getElementById('historyToggle').addEventListener('click', () => {
  document.getElementById('historySidebar').classList.toggle('open');
  document.getElementById('historyBackdrop').classList.toggle('show');
  renderHistory();
});

// Render history list
function renderHistory() {
  const historyList = document.getElementById('historyList');
  const entries = history.getAll();

  if (entries.length === 0) {
    historyList.innerHTML = '<div class="empty-state">No calculations yet</div>';
    return;
  }

  historyList.innerHTML = entries.map(entry => `
    <div class="history-entry" data-id="${entry.id}">
      <div class="entry-timestamp">${formatRelativeTime(entry.timestamp)}</div>
      <div class="entry-summary">
        ${entry.metadata.sex} • ${entry.metadata.ageYears}y
      </div>
      <div class="entry-measurements">
        ${formatMeasurements(entry.metadata)}
      </div>
      <div class="entry-actions">
        <button class="btn-load" data-id="${entry.id}">Load</button>
        <button class="btn-delete" data-id="${entry.id}" aria-label="Delete">🗑️</button>
      </div>
    </div>
  `).join('');

  // Update badge
  document.getElementById('historyCount').textContent = entries.length;
}

// Load entry
function loadHistoryEntry(id) {
  const entry = history.get(id);
  if (!entry) return;

  // Populate form
  Object.keys(entry.formData).forEach(key => {
    const input = document.getElementById(key);
    if (input) {
      if (input.type === 'radio') {
        const radio = document.querySelector(`input[name="${key}"][value="${entry.formData[key]}"]`);
        if (radio) radio.checked = true;
      } else {
        input.value = entry.formData[key];
      }
    }
  });

  // Display results
  displayResults(entry.results);

  // Close sidebar
  document.getElementById('historySidebar').classList.remove('open');
}

// Save after successful calculation
async function handleFormSubmit(e) {
  // ... existing calculation logic ...

  if (response.ok) {
    const data = await response.json();

    // Save to history
    const formData = getFormData();  // Extract all form data
    history.add(formData, data);

    // ... display results ...
  }
}
```

### Phase 3: Integration & Testing (1-2 hours)

**Tests to Add:**
```javascript
// tests/test_history.js

describe('CalculationHistory', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('adds new entry', () => {
    const history = new CalculationHistory();
    history.add(mockFormData, mockResults);
    expect(history.getAll()).toHaveLength(1);
  });

  test('respects max entries limit', () => {
    const history = new CalculationHistory(3);
    for (let i = 0; i < 5; i++) {
      history.add(mockFormData, mockResults);
    }
    expect(history.getAll()).toHaveLength(3);
  });

  test('prevents duplicate consecutive entries', () => {
    const history = new CalculationHistory();
    history.add(mockFormData, mockResults);
    history.add(mockFormData, mockResults);  // Same data
    expect(history.getAll()).toHaveLength(1);
  });

  test('deletes specific entry', () => {
    const history = new CalculationHistory();
    history.add(mockFormData, mockResults);
    const id = history.getAll()[0].id;
    history.delete(id);
    expect(history.getAll()).toHaveLength(0);
  });
});
```

**Manual Testing Checklist:**
- [ ] Save calculation to history
- [ ] Load calculation from history
- [ ] Delete individual entry
- [ ] Clear all history
- [ ] History persists after page reload
- [ ] History badge updates correctly
- [ ] Mobile responsive (sidebar full-width)
- [ ] Keyboard navigation works
- [ ] Works with all form fields (parental heights, gestation, etc.)
- [ ] Doesn't save duplicates
- [ ] Handles edge cases (no measurements, errors, etc.)

## Edge Cases & Error Handling

1. **localStorage Full**
   - Catch QuotaExceededError
   - Show user-friendly message
   - Offer to clear old entries

2. **Corrupted Data**
   - Validate data structure on load
   - Reset to empty if invalid
   - Log error (console)

3. **Privacy Mode**
   - Check if localStorage available
   - Disable history in privacy mode
   - Show notice to user

4. **Failed Calculations**
   - Don't save failed/error calculations
   - Only save successful results

5. **Partial Form Data**
   - Handle optional fields gracefully
   - Don't fail on missing optional data

## Accessibility

- [x] ARIA labels for buttons
- [x] Role="dialog" for sidebar
- [x] Keyboard navigation (Tab, Enter, Escape)
- [x] Focus management (trap focus in sidebar when open)
- [x] Screen reader announcements for actions
- [x] Sufficient color contrast (4.5:1 minimum)

## Performance Considerations

- Lazy render history (only when sidebar opens)
- Debounce rapid saves
- Use document fragment for batch rendering
- Minimize localStorage writes
- Cache parsed history in memory

## Security & Privacy

- Don't include identifiable patient data in storage (no names/MRN)
- Clear localStorage on app uninstall/clear data
- Respect Do Not Track header (future)
- Allow user to disable history entirely (future)

## Migration Strategy

- Version field in storage format
- Graceful handling of old versions
- Auto-migrate on load if needed

## Future Enhancements (Post-MVP)

- Export history to file
- Search/filter history
- Sort by date/sex/age
- Tags/notes for entries
- Favorite/pin important calculations
- Sync across devices (cloud)
- Share history entry (secure link)

## Success Metrics

- 60%+ of users with >1 history entry
- Average 3-5 history entries per active user
- <2% localStorage quota errors
- Positive user feedback on workflow improvement

## Timeline

- **Day 1 Morning**: Data layer implementation + unit tests
- **Day 1 Afternoon**: UI components (HTML/CSS)
- **Day 2 Morning**: JavaScript integration + event handlers
- **Day 2 Afternoon**: Testing + bug fixes + documentation

## Dependencies

- None (pure localStorage + vanilla JS)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| localStorage disabled | High | Detect and show warning, disable feature gracefully |
| Storage quota exceeded | Medium | Reduce max entries, offer clear option |
| Performance on mobile | Low | Optimize rendering, lazy load |

## Open Questions

1. ✅ Should we show results preview in history? **Yes, show key measurements**
2. ✅ Include charts in history? **No, too much data - recalculate on load**
3. ✅ Allow export of single history entry? **Future enhancement**
4. ✅ Keyboard shortcut to open history (H key)? **Yes, add in Phase 2**

---

**Next Steps:**
1. Review and approve this plan
2. Create feature branch: `feature/calculation-history`
3. Implement Phase 1 (data layer)
4. Implement Phase 2 (UI)
5. Testing & refinement
6. Merge to main
