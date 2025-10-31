# Frontend Service

React Router 7 + Vite frontend application for the Healthcare Support Portal.

## Technology Stack

- **Framework**: React Router 7 (Framework Mode)
- **Build Tool**: Vite 6
- **Styling**: TailwindCSS v4 (Zero Config)
- **UI Components**: shadcn/ui with Radix UI primitives
- **State Management**: React Context + TanStack Query
- **HTTP Client**: Axios
- **TypeScript**: Full type safety
- **Icons**: Lucide React

## Features

- **Authentication**: JWT-based login/signup with role-based access
- **Dashboard**: Role-specific overview with quick actions and stats
- **Patient Management**: CRUD operations for patient records
- **Chat Assistant**: AI-powered medical Q&A with RAG integration
- **Document Management**: Upload, search, and manage medical documents
- **Responsive Design**: Mobile-first design with desktop navigation
- **Role-Based UI**: Different interfaces for doctor/nurse/admin roles
- **Real-time Notifications**: Toast notifications for user feedback

## Getting Started

### Prerequisites

- Node.js 20.19+ (required by Vite 7)
- Backend services running (auth, patient, RAG services)
- PostgreSQL database with healthcare data

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

### Environment Variables

Edit `.env` file:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost
VITE_AUTH_SERVICE_PORT=8001
VITE_PATIENT_SERVICE_PORT=8002
VITE_RAG_SERVICE_PORT=8003

# App Configuration
VITE_APP_NAME="Healthcare Support Portal"
VITE_APP_VERSION="0.1.0"

# Development
VITE_DEBUG=true
```

## Development

### Available Scripts

```bash
npm run dev       # Start development server
npm run build     # Build for production
npm run start     # Start production server
npm run typecheck # Run TypeScript checks
npm run lint      # Run ESLint
```

### Key Directories

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui components
│   └── Navigation.tsx   # Main navigation component
├── lib/                 # Utilities and configuration
│   ├── api.ts          # API client with axios
│   ├── auth.ts         # Authentication context
│   ├── types.ts        # TypeScript type definitions
│   └── utils.ts        # Utility functions
├── routes/             # React Router 7 route components
│   ├── _layout.tsx     # Root layout with auth
│   ├── dashboard.tsx   # Dashboard page
│   ├── login.tsx       # Login page
│   ├── signup.tsx      # Registration page
│   ├── chat.tsx        # AI chat interface
│   ├── documents.tsx   # Document management
│   └── patients/       # Patient management pages
└── styles/
    └── globals.css     # TailwindCSS v4 styles
```

## Authentication Flow

1. **Login/Signup**: JWT token stored in localStorage
2. **Route Protection**: `_layout.tsx` checks authentication
3. **API Integration**: Axios interceptors add auth headers
4. **Role-Based Access**: UI adapts based on user role
5. **Token Refresh**: Automatic token refresh before expiration

## API Integration

The frontend connects to three backend services:

- **Auth Service (8001)**: User authentication and management
- **Patient Service (8002)**: Patient CRUD operations
- **RAG Service (8003)**: Document management and AI chat

API client (`src/lib/api.ts`) provides typed methods for all endpoints.

## UI Components

Built with shadcn/ui for consistent, accessible components:

- **Forms**: Login, signup, patient creation
- **Navigation**: Responsive sidebar with role-based menu items
- **Cards**: Patient cards, document cards, dashboard stats
- **Tables**: Patient lists, document lists (future enhancement)
- **Chat Interface**: Real-time AI conversation with sources
- **Badges**: Role indicators, status badges, department tags

## Styling

TailwindCSS v4 with zero configuration:

- **Custom Theme**: Healthcare-specific colors and spacing
- **Role-Based Styling**: Different colors for doctor/nurse/admin
- **Department Indicators**: Color-coded department borders
- **Responsive Design**: Mobile-first with desktop enhancements
- **Accessibility**: High contrast mode, reduced motion support

## Deployment

### Development

```bash
# Start all services including frontend
./run_all.sh
```

Visit http://localhost:3000

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start
```

## Demo Credentials

For testing, use these demo accounts:

- **Doctor**: `dr_smith` / `secure_password`
- **Nurse**: `nurse_johnson` / `secure_password`
- **Admin**: `admin_doe` / `secure_password`

## Architecture Notes

- **React Router 7**: Uses framework mode for enhanced features
- **Vite 6**: Fast development with HMR and optimized builds
- **TailwindCSS v4**: Zero-config setup with CSS-first customization
- **Type Safety**: Full TypeScript coverage for API and UI
- **State Management**: Context for auth, TanStack Query for server state
- **Error Handling**: Comprehensive error boundaries and user feedback

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Modern browsers with ES2022 support required.