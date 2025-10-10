# Wealth Coach AI - Frontend Application

A beautiful, production-ready UI for the Wealth Coach AI application featuring modern design patterns, smooth animations, and a comprehensive user experience.

## Features

### Authentication
- **Login Page** - Secure email/password authentication with beautiful gradient backgrounds
- **Registration** - New user signup with validation and immediate onboarding flow
- Protected routes with automatic redirection

### Onboarding Experience
- **Multi-step Form** - 3-step progressive onboarding process
  - Step 1: Financial Goals (text area for detailed input)
  - Step 2: Risk Tolerance (conservative/moderate/aggressive)
  - Step 3: Income & Expenses (with automatic savings calculation)
- Progress indicators and smooth transitions between steps
- Form validation and error handling

### Chat Interface
- **Real-time Streaming** - Token-by-token AI response streaming via SSE
- **Conversation History** - Persistent chat history stored in localStorage
- **Sidebar Navigation** - Collapsible sidebar with:
  - New conversation creation
  - Chat history browsing
  - User profile display
  - Logout functionality
- **Message Display** - Distinct styling for user and AI messages
- **Suggested Questions** - Quick-start prompts for new users
- **Responsive Design** - Mobile-friendly with collapsible sidebar

## Design Features

### Visual Design
- **Gradient Backgrounds** - Animated blue/purple gradient (finance theme)
- **Glass Morphism** - Frosted glass effects with backdrop blur
- **Smooth Animations** - Fade-in, slide-up, and slide-in transitions
- **Custom Icons** - Lucide React icons throughout
- **Professional Color Scheme** - Primary blues and accent purples

### UI Components
- **Button** - Multiple variants (default, secondary, outline, ghost, danger)
- **Input** - Styled form inputs with focus states and validation
- **Card** - Glass-morphic card containers with modular sections
- **Label** - Consistent form labels

### Technical Features
- **TypeScript-ready** - Clean component structure
- **Tailwind CSS 4.x** - Modern utility-first styling
- **React Router** - Client-side routing with route protection
- **localStorage** - Persistent user data and chat history
- **Error Handling** - Comprehensive error states and user feedback

## File Structure

```
src/
├── components/
│   ├── Button.jsx        # Reusable button component with variants
│   ├── Card.jsx          # Card container with header/content/footer
│   ├── Input.jsx         # Form input with validation states
│   └── Label.jsx         # Form label component
├── pages/
│   ├── LoginPage.jsx     # Authentication page
│   ├── RegisterPage.jsx  # User registration
│   ├── OnboardingPage.jsx # Multi-step onboarding
│   └── ChatPage.jsx      # Main chat interface
├── lib/
│   └── utils.js          # Utility functions (cn helper)
├── App.jsx               # Main app with routing
├── main.jsx              # React entry point
└── index.css             # Global styles and Tailwind config
```

## API Integration

### Endpoints Used
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Authenticate existing user
- `POST /api/v1/onboarding` - Save user financial profile
- `POST /api/v1/chat/message/stream` - Send messages and receive streaming responses

### Authentication
- JWT tokens stored in localStorage
- Bearer token authentication on protected endpoints
- Automatic token validation and redirect

### Streaming Implementation
- Server-Sent Events (SSE) for real-time responses
- Token-by-token rendering for smooth UX
- Conversation ID management for chat history

## Running the Application

### Development
```bash
npm run dev
```
Runs on http://localhost:5173 with Vite proxy to backend on port 8000.

### Build
```bash
npm run build
```
Creates production-ready build in `dist/` directory.

### Preview
```bash
npm run preview
```
Preview production build locally.

## Environment Requirements

- Node.js 18+ recommended
- Backend API running on http://localhost:8000
- Modern browser with ES6+ support

## Configuration

### Vite Proxy
The application uses Vite's proxy feature to forward `/api` requests to the backend:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Tailwind CSS 4.x
Custom theme configuration in `src/index.css` using the new `@theme` directive:
- Custom primary/accent color palettes
- Animation definitions
- Utility class extensions

## User Flow

1. **First Visit** → Login/Register page
2. **New User Registration** → Immediate redirect to Onboarding
3. **Onboarding Completion** → Redirect to Chat
4. **Returning User Login** → Direct to Chat (if onboarded) or Onboarding (if not)
5. **Chat Session** → Access to full chat interface with history

## State Management

- **Authentication** - localStorage for tokens and user data
- **Onboarding Status** - localStorage flag for completion
- **Chat History** - localStorage for conversation persistence
- **UI State** - React hooks for local component state

## Responsive Design

- Mobile-first approach
- Collapsible sidebar on mobile
- Touch-friendly button sizes
- Adaptive layouts for all screen sizes
- Tested on common viewport dimensions

## Performance Optimizations

- Lazy loading with React Router
- Optimized re-renders with proper React patterns
- Efficient streaming implementation
- Minimal bundle size with tree-shaking
- CSS purging in production builds

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- Dark/light mode toggle
- Voice input for messages
- Export chat transcripts
- Advanced financial visualizations
- Multi-language support
- Offline mode with service workers

## Credits

Built with:
- React 19
- Tailwind CSS 4.x
- Vite 7
- Lucide React Icons
- React Router 7
