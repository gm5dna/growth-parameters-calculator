/**
 * Jest Setup File
 *
 * Configures the testing environment with necessary mocks and polyfills
 * for browser APIs that aren't available in Jest's jsdom environment.
 */

// Mock localStorage
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock sessionStorage
global.sessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock Clipboard API
Object.defineProperty(navigator, 'clipboard', {
  writable: true,
  value: {
    writeText: jest.fn(() => Promise.resolve()),
    readText: jest.fn(() => Promise.resolve('')),
  },
});

// Mock document.execCommand for fallback clipboard
document.execCommand = jest.fn(() => true);

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    status: 200,
    statusText: 'OK',
  })
);

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Reset mocks before each test
beforeEach(() => {
  if (localStorage.getItem.mockClear) {
    localStorage.getItem.mockClear();
    localStorage.setItem.mockClear();
    localStorage.removeItem.mockClear();
    localStorage.clear.mockClear();
  }

  if (sessionStorage.getItem.mockClear) {
    sessionStorage.getItem.mockClear();
    sessionStorage.setItem.mockClear();
    sessionStorage.removeItem.mockClear();
    sessionStorage.clear.mockClear();
  }

  if (navigator.clipboard && navigator.clipboard.writeText.mockClear) {
    navigator.clipboard.writeText.mockClear();
    navigator.clipboard.readText.mockClear();
  }

  if (fetch.mockClear) {
    fetch.mockClear();
  }

  if (document.execCommand.mockClear) {
    document.execCommand.mockClear();
  }
});
