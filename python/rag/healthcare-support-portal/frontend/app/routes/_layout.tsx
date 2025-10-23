import { Outlet, useLoaderData, redirect } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigation } from "@/components/Navigation";
import { Toaster } from "@/components/ui/toaster";
import { getCurrentUser } from "@/lib/utils/loader-utils";
import type { User } from "@/lib/types";
import type { LoaderFunctionArgs } from 'react-router';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Loader function - check authentication and provide user data
export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  console.log(`[Layout] Loading ${pathname}`);
  
  // Define public routes that don't require authentication
  const publicRoutes = ['/login', '/signup'];
  const isPublicRoute = publicRoutes.includes(pathname);
  
  const user = await getCurrentUser(request);
  
  console.log(`[Layout] User: ${user ? `${user.username} (${user.role})` : 'none'}, Public route: ${isPublicRoute}`);
  
  // If not authenticated and trying to access protected route, redirect to login
  if (!user && !isPublicRoute) {
    console.log(`[Layout] Redirecting to login: no user for protected route ${pathname}`);
    throw redirect('/login');
  }
  
  // If authenticated and trying to access auth pages, redirect to dashboard
  if (user && isPublicRoute) {
    console.log(`[Layout] Redirecting to dashboard: authenticated user accessing ${pathname}`);
    throw redirect('/');
  }
  
  console.log(`[Layout] Allowing access to ${pathname}`);
  return { user, isPublicRoute };
}

interface LayoutData {
  user: User | null;
  isPublicRoute: boolean;
}

function LayoutContent() {
  const { user, isPublicRoute } = useLoaderData<LayoutData>();

  // Render layout for authenticated users
  if (user && !isPublicRoute) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation user={user} />
        <main className="lg:pl-64">
          <div className="px-4 sm:px-6 lg:px-8 py-8">
            <Outlet />
          </div>
        </main>
        <Toaster />
      </div>
    );
  }

  // Render auth pages without navigation
  return (
    <div className="min-h-screen bg-gray-50">
      <Outlet />
      <Toaster />
    </div>
  );
}

export default function Layout() {
  return (
    <QueryClientProvider client={queryClient}>
      <LayoutContent />
    </QueryClientProvider>
  );
}