# Quick Start Guide

## Prerequisites

1. **Backend API must be running on http://localhost:8000**
2. Node.js 18+ installed
3. npm installed

## Installation

Already installed! Dependencies are in place.

## Running the Application

### Start Development Server
```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

## Using the Application

### 1. Create an Account
- Navigate to http://localhost:5173
- You'll be redirected to the login page
- Click "Sign up" to create a new account
- Fill in:
  - Full Name
  - Email
  - Password (minimum 6 characters)
  - Confirm Password

### 2. Complete Onboarding
After registration, you'll be taken through a 3-step onboarding:

**Step 1: Financial Goals**
- Enter your financial goals (e.g., "Save for retirement, buy a house, build emergency fund")

**Step 2: Risk Tolerance**
- Select your risk tolerance:
  - Conservative: Safety and stability
  - Moderate: Balanced approach
  - Aggressive: Higher risk for potential gains

**Step 3: Income & Expenses**
- Enter your monthly income
- Enter your monthly expenses
- See your savings potential calculated automatically

### 3. Start Chatting
Once onboarding is complete, you'll land on the chat interface:

- **New Conversation**: Click the "New Conversation" button in the sidebar
- **Ask Questions**: Type your financial questions in the input box
- **Suggested Prompts**: Click any of the suggested questions to get started
- **Chat History**: Access previous conversations from the sidebar
- **Streaming Responses**: Watch as the AI responds in real-time

### Example Questions to Ask
- "How should I start investing?"
- "Help me create a budget"
- "What is a good emergency fund size?"
- "Should I pay off debt or invest?"
- "How can I save for retirement?"

## Features Overview

### Authentication
- Secure JWT-based authentication
- Password validation
- Auto-redirect based on onboarding status

### Chat Interface
- Real-time streaming AI responses
- Persistent chat history (stored locally)
- Sidebar with conversation management
- Mobile-responsive design
- Collapsible sidebar for mobile

### Design Elements
- Animated gradient backgrounds
- Glass morphism effects
- Smooth transitions and animations
- Professional financial theme (blues/purples)

## Troubleshooting

### Backend Not Running
**Error**: API requests fail with network errors

**Solution**: Make sure the backend is running on http://localhost:8000
```bash
# Start your backend server
# The frontend expects it on port 8000
```

### Port Already in Use
**Error**: Port 5173 is already in use

**Solution**:
1. Kill the process using port 5173, or
2. Vite will automatically use the next available port

### Login/Registration Not Working
**Error**: "Login failed" or "Registration failed"

**Solution**:
1. Check that backend is running
2. Check browser console for specific errors
3. Verify API endpoints are responding:
   - http://localhost:8000/api/v1/auth/register
   - http://localhost:8000/api/v1/auth/login

### Chat Responses Not Streaming
**Error**: Messages send but no response appears

**Solution**:
1. Check browser console for errors
2. Verify the streaming endpoint is working:
   - POST http://localhost:8000/api/v1/chat/message/stream
3. Check that you're logged in (token in localStorage)

### Styles Not Loading
**Error**: Page looks unstyled

**Solution**:
1. Stop the dev server (Ctrl+C)
2. Clear node_modules: `rm -rf node_modules`
3. Reinstall: `npm install`
4. Restart: `npm run dev`

## Local Storage Data

The app stores data in browser localStorage:
- `token`: JWT authentication token
- `user`: User information (email, name)
- `hasOnboarded`: Onboarding completion flag
- `conversations`: Chat history

### Clear Local Data
To reset the app and start fresh:
```javascript
// In browser console
localStorage.clear();
location.reload();
```

## Production Build

### Build for Production
```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

This serves the production build locally for testing.

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Page components (Login, Chat, etc)
├── lib/             # Utility functions
├── App.jsx          # Main app with routing
├── main.jsx         # React entry point
└── index.css        # Global styles & Tailwind
```

## API Endpoints

All API calls go through Vite proxy to avoid CORS issues:

- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/onboarding` - Save onboarding data
- `POST /api/v1/chat/message/stream` - Send messages (SSE)

## Development Tips

### Hot Module Replacement
Changes to components will auto-reload without losing state.

### React DevTools
Install React DevTools browser extension for better debugging.

### Network Tab
Use browser DevTools → Network tab to debug API calls.

### Console Logging
Check browser console for streaming events and errors.

## Next Steps

After getting familiar with the basic features:

1. Explore different types of financial questions
2. Test the conversation history feature
3. Try the mobile responsive design
4. Test the onboarding flow with different inputs
5. Experiment with various risk tolerance settings

## Support

For issues or questions:
1. Check the main README_UI.md for detailed documentation
2. Review the troubleshooting section above
3. Check browser console for error messages
4. Verify backend API is running and accessible

---

**Happy financial planning!** 🚀💰
