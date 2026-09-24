import '@testing-library/jest-dom/vitest';
import * as matchers from 'vitest-axe/matchers';
import { server } from '../mocks/server';

expect.extend(matchers);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// jsdom lacks these; components only call them in user-triggered paths.
Object.defineProperty(window, 'scrollTo', { value: () => {}, writable: true });
if (!('clipboard' in navigator)) {
  Object.defineProperty(navigator, 'clipboard', {
    value: { writeText: async () => {} },
    configurable: true,
  });
}
