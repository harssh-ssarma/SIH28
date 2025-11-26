/**
 * Enterprise JWT Authentication with Auto-Refresh
 * Handles token refresh, retry logic, and session management
 */

interface TokenResponse {
  access: string;
  refresh: string;
}

let refreshPromise: Promise<string> | null = null;

/**
 * Get access token with auto-refresh if expired
 */
export async function getAccessToken(): Promise<string | null> {
  // Check if we're in browser environment
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return null;
  }

  try {
    // Check both 'token' and 'access_token' for compatibility
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    if (!token) return null;

    // Check if token is expired or about to expire (within 5 minutes)
    if (isTokenExpiringSoon(token)) {
      return await refreshAccessToken();
    }

    return token;
  } catch (error) {
    console.error('Error getting access token:', error);
    return null;
  }
}

/**
 * Check if JWT token is expiring soon (within 5 minutes)
 */
function isTokenExpiringSoon(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;
    return exp - now < fiveMinutes;
  } catch {
    return true; // If can't parse, assume expired
  }
}

/**
 * Refresh access token using refresh token
 * Prevents multiple simultaneous refresh requests
 */
async function refreshAccessToken(): Promise<string | null> {
  // Check if we're in browser environment
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return null;
  }

  // If refresh already in progress, wait for it
  if (refreshPromise) {
    return await refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken') || localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.warn('No refresh token available');
        return null;
      }

      const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        console.warn('Token refresh failed with status:', response.status);
        return null;
      }

      const data: TokenResponse = await response.json();
      localStorage.setItem('token', data.access);
      localStorage.setItem('access_token', data.access);
      
      // Update refresh token if provided
      if (data.refresh) {
        localStorage.setItem('refreshToken', data.refresh);
        localStorage.setItem('refresh_token', data.refresh);
      }

      return data.access;
    } catch (error) {
      console.error('Token refresh error:', error);
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return await refreshPromise;
}

/**
 * Make authenticated API request with auto-retry on 401
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // Try to get token, but don't fail if not available
  let token = await getAccessToken();
  
  // If no token, try to get it from localStorage directly (fallback)
  if (!token && typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      token = localStorage.getItem('token') || localStorage.getItem('access_token');
    } catch (e) {
      console.error('Error accessing localStorage:', e);
    }
  }
  
  if (!token) {
    // Instead of throwing, try the request without auth (some endpoints might not require it)
    console.warn('No authentication token available, attempting request without auth');
    return await fetch(url, options);
  }

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  let response = await fetch(url, { ...options, headers });

  // If 401, try refreshing token once and retry
  if (response.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      response = await fetch(url, { ...options, headers });
    } else {
      // If refresh failed, try without auth as last resort
      console.warn('Token refresh failed, attempting request without auth');
      response = await fetch(url, options);
    }
  }

  return response;
}

/**
 * Store tokens after login
 */
export function storeTokens(access: string, refresh: string): void {
  localStorage.setItem('token', access);
  localStorage.setItem('access_token', access); // Compatibility
  localStorage.setItem('refreshToken', refresh);
  localStorage.setItem('refresh_token', refresh); // Compatibility
}

/**
 * Clear tokens on logout
 */
export function clearTokens(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('refresh_token');
}
