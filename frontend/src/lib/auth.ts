/**
 * Google-Like Secure Authentication with HttpOnly Cookies
 * NO localStorage - tokens stored in secure HttpOnly cookies only
 * Auto-refresh handled by backend cookie rotation
 */

let refreshPromise: Promise<boolean> | null = null;

/**
 * 🔐 SECURE: Refresh using HttpOnly cookies (NO localStorage)
 * Backend automatically rotates tokens and sets new cookies
 */
async function refreshAccessTokenViaCookie(): Promise<boolean> {
  // If refresh already in progress, wait for it
  if (refreshPromise) {
    return await refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      
      const response = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        credentials: 'include', // 🔐 Send HttpOnly cookies
        headers: { 'Content-Type': 'application/json' },
      });

      return response.ok;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return await refreshPromise;
}/**
 * 🔐 SECURE: Cookie-based authenticated fetch (Google-like)
 * Tokens sent automatically via HttpOnly cookies
 * NO manual token handling - prevents XSS attacks
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // 🔐 CRITICAL: credentials: 'include' sends HttpOnly cookies
  const fetchOptions: RequestInit = {
    ...options,
    credentials: 'include', // Send cookies with every request
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  let response = await fetch(url, fetchOptions);

  // If 401, try refreshing token once via cookie and retry
  if (response.status === 401 && !url.includes('/auth/refresh')) {
    const refreshed = await refreshAccessTokenViaCookie();
    if (refreshed) {
      // Retry original request (new cookies set by refresh endpoint)
      response = await fetch(url, fetchOptions);
    }
  }

  return response;
}

/**
 * 🔐 DEPRECATED: No token storage needed with HttpOnly cookies
 * Tokens are managed by backend via secure cookies
 */
export function storeTokens(access: string, refresh: string): void {
  // No-op: Tokens stored in HttpOnly cookies by backend
  console.info('✅ Tokens stored in secure HttpOnly cookies');
}

/**
 * 🔐 Tokens cleared by backend (cookie deletion)
 * This function only clears user data from localStorage
 */
export function clearTokens(): void {
  // Clear user data (not tokens - they're in HttpOnly cookies)
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    localStorage.removeItem('user');
  }
}
