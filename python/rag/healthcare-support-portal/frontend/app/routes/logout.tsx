import { redirect } from 'react-router';
import { clearAuthCookies } from '@/lib/utils/action-utils';
import type { ActionFunctionArgs } from 'react-router';

// Action function - handle logout
export async function action({ request }: ActionFunctionArgs) {
  // Clear auth cookies and redirect to login
  return clearAuthCookies();
}

// This route should never render - it's action-only
export default function Logout() {
  return null;
}