/**
 * Pseudonymous session token stored in localStorage.
 * NOT a secure authentication system — just a research tool convenience.
 */

const KEY = 'eia_planner_token'

function generateToken(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID().replace(/-/g, '')
  }
  // Fallback for older environments
  return Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join('')
}

export function getOrCreateToken(): string {
  let token = localStorage.getItem(KEY)
  if (!token) {
    token = generateToken()
    localStorage.setItem(KEY, token)
  }
  return token
}

export function clearToken(): void {
  localStorage.removeItem(KEY)
}
