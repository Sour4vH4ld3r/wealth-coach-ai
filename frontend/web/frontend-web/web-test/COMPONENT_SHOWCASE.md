# Component Showcase

## Visual Design Elements

### Color Palette

**Primary (Blues)**
- primary-400: #38bdf8 (Light Blue)
- primary-500: #0ea5e9 (Sky Blue)
- primary-600: #0284c7 (Ocean Blue)
- primary-700: #0369a1 (Deep Blue)

**Accent (Purples)**
- accent-400: #c084fc (Light Purple)
- accent-500: #a855f7 (Purple)
- accent-600: #9333ea (Deep Purple)
- accent-700: #7e22ce (Royal Purple)

**Finance Gradient**
Blue → Purple → Pink gradient for backgrounds

### Typography
- Font Family: System UI stack
- Headings: Bold, large, white
- Body: Regular, readable, white/white-70
- Labels: Medium weight, white-90

## Component Gallery

### Button Component
```jsx
import Button from './components/Button';

// Default variant (gradient)
<Button>Sign In</Button>

// Secondary (transparent with border)
<Button variant="secondary">Cancel</Button>

// Outline
<Button variant="outline">Learn More</Button>

// Ghost (minimal)
<Button variant="ghost">Skip</Button>

// Danger
<Button variant="danger">Delete</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon /></Button>

// States
<Button disabled>Loading...</Button>
<Button onClick={handleClick}>Click Me</Button>
```

**Visual Features:**
- Gradient backgrounds (blue to deeper blue)
- Shadow effects (shadow-primary-500/30)
- Hover state transitions
- Focus ring (ring-2 ring-primary-500)
- Disabled opacity (opacity-50)
- Rounded corners (rounded-lg)

---

### Input Component
```jsx
import Input from './components/Input';

// Basic input
<Input 
  type="text" 
  placeholder="Enter text..."
/>

// Email input
<Input 
  type="email" 
  placeholder="your@email.com"
/>

// Password input
<Input 
  type="password" 
  placeholder="Password"
/>

// With error state
<Input 
  error={true}
  placeholder="Invalid input"
/>

// With icon (custom wrapper)
<div className="relative">
  <Mail className="absolute left-3 top-1/2 -translate-y-1/2" />
  <Input className="pl-11" />
</div>
```

**Visual Features:**
- Glass morphism (bg-white/5, backdrop-blur)
- Border with opacity (border-white/20)
- Focus ring (ring-2 ring-primary-500)
- Placeholder styling (text-white/50)
- Error state (red border and ring)
- Smooth transitions

---

### Card Component
```jsx
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription,
  CardContent,
  CardFooter 
} from './components/Card';

// Complete card
<Card>
  <CardHeader>
    <CardTitle>Welcome</CardTitle>
    <CardDescription>Get started with your account</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Your content here */}
  </CardContent>
  <CardFooter>
    <Button>Continue</Button>
  </CardFooter>
</Card>
```

**Visual Features:**
- Glass morphism (frosted glass effect)
- Backdrop blur (backdrop-blur-xl)
- Subtle border (border-white/20)
- Large shadow (shadow-2xl)
- Rounded corners (rounded-xl)
- Hover effect (shadow changes)
- Modular sections (header, content, footer)

---

### Label Component
```jsx
import Label from './components/Label';

// Basic label
<Label htmlFor="email">Email Address</Label>

// With input
<div className="space-y-2">
  <Label htmlFor="password">Password</Label>
  <Input id="password" type="password" />
</div>
```

**Visual Features:**
- Small text (text-sm)
- Medium weight (font-medium)
- White with opacity (text-white/90)
- Peer disabled support

---

## Page Designs

### LoginPage
**Layout:**
```
┌─────────────────────────────────────┐
│   Animated Gradient Background      │
│                                     │
│         [Icon] Wealth Coach AI      │
│     Your Personal Financial...      │
│                                     │
│   ┌───────────────────────────┐   │
│   │  Welcome Back             │   │
│   │  Sign in to continue...   │   │
│   │                           │   │
│   │  Email    [__________]    │   │
│   │  Password [__________]    │   │
│   │                           │   │
│   │  [Sign In Button]         │   │
│   │                           │   │
│   │  Don't have account?      │   │
│   │  Sign up                  │   │
│   └───────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Colors:** Blue-purple gradient with glass card
**Animations:** Fade in, slide up
**Icons:** TrendingUp, Mail, Lock

---

### RegisterPage
**Layout:**
```
┌─────────────────────────────────────┐
│   Animated Gradient Background      │
│                                     │
│         [Icon] Wealth Coach AI      │
│   Start your journey to...          │
│                                     │
│   ┌───────────────────────────┐   │
│   │  Create Account           │   │
│   │  Get started with...      │   │
│   │                           │   │
│   │  Full Name [_________]    │   │
│   │  Email     [_________]    │   │
│   │  Password  [_________]    │   │
│   │  Confirm   [_________]    │   │
│   │                           │   │
│   │  [Create Account]         │   │
│   │                           │   │
│   │  Already have account?    │   │
│   │  Sign in                  │   │
│   └───────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Colors:** Same gradient as login
**Animations:** Fade in, slide up
**Icons:** TrendingUp, User, Mail, Lock

---

### OnboardingPage
**Layout (3 Steps):**
```
Step 1: Financial Goals
┌─────────────────────────────────────┐
│   Let's Get Started                 │
│   Help us personalize...            │
│                                     │
│   ┌───────────────────────────┐   │
│   │ Step 1 of 3    [▓▓▒▒▒▒]  │   │
│   │ Tell us about...          │   │
│   │                           │   │
│   │      [Target Icon]        │   │
│   │                           │   │
│   │ What are your financial   │   │
│   │ goals?                    │   │
│   │ ┌──────────────────────┐ │   │
│   │ │                      │ │   │
│   │ │  [Text Area]         │ │   │
│   │ │                      │ │   │
│   │ └──────────────────────┘ │   │
│   │                           │   │
│   │              [Next →]     │   │
│   └───────────────────────────┘   │
└─────────────────────────────────────┘

Step 2: Risk Tolerance
┌─────────────────────────────────────┐
│   ┌───────────────────────────┐   │
│   │ Step 2 of 3    [▓▓▓▓▒▒]  │   │
│   │                           │   │
│   │    [TrendingUp Icon]      │   │
│   │                           │   │
│   │ ○ Conservative            │   │
│   │   Prefer safety...        │   │
│   │                           │   │
│   │ ● Moderate                │   │
│   │   Balanced approach...    │   │
│   │                           │   │
│   │ ○ Aggressive              │   │
│   │   Comfortable with...     │   │
│   │                           │   │
│   │  [← Back]     [Next →]    │   │
│   └───────────────────────────┘   │
└─────────────────────────────────────┘

Step 3: Income & Expenses
┌─────────────────────────────────────┐
│   ┌───────────────────────────┐   │
│   │ Step 3 of 3    [▓▓▓▓▓▓]  │   │
│   │                           │   │
│   │    [DollarSign Icon]      │   │
│   │                           │   │
│   │ Monthly Income            │   │
│   │ $ [___________]           │   │
│   │                           │   │
│   │ Monthly Expenses          │   │
│   │ $ [___________]           │   │
│   │                           │   │
│   │ ┌─────────────────────┐  │   │
│   │ │ Savings Potential   │  │   │
│   │ │ $ 2,000.00          │  │   │
│   │ └─────────────────────┘  │   │
│   │                           │   │
│   │  [← Back]   [Complete ✓]  │   │
│   └───────────────────────────┘   │
└─────────────────────────────────────┘
```

**Features:**
- Progress bar with steps
- Step indicators
- Icon changes per step
- Smooth transitions (slide-in)
- Back/Next navigation
- Real-time calculation

---

### ChatPage
**Layout:**
```
┌──────────────────────────────────────────────┐
│  Sidebar (280px)  │  Chat Area              │
├───────────────────┼──────────────────────────┤
│ [≡] Wealth Coach │  [≡] New Conversation    │
│                   │                          │
│ [+ New Conv]      │  ┌──────────────────┐   │
│                   │  │ [Bot] Welcome!   │   │
│ • Chat 1          │  │ How can I help?  │   │
│ • Chat 2          │  └──────────────────┘   │
│ • Chat 3          │                          │
│                   │  ┌──────────────────┐   │
│                   │  │ How to invest? │   │
│                   │  │           [User] │   │
│                   │  └──────────────────┘   │
│                   │                          │
│                   │  ┌──────────────────┐   │
│                   │  │ [Bot] Great      │   │
│ [User]            │  │ question! Here's │   │
│ John Doe          │  │ my advice...     │   │
│ [Logout]          │  └──────────────────┘   │
│                   │                          │
│                   │  [Type message...] [→]   │
└───────────────────┴──────────────────────────┘
```

**Features:**
- Collapsible sidebar
- Chat history list
- New conversation button
- Message bubbles (distinct for user/AI)
- Streaming animation (typing effect)
- Auto-scroll to bottom
- Empty state with suggestions
- Mobile responsive (sidebar collapses)

---

## Animation Showcase

### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```
Used on: Page loads

### Slide Up
```css
@keyframes slideUp {
  from { 
    transform: translateY(20px); 
    opacity: 0; 
  }
  to { 
    transform: translateY(0); 
    opacity: 1; 
  }
}
```
Used on: Cards, modals

### Slide In
```css
@keyframes slideIn {
  from { 
    transform: translateX(-20px); 
    opacity: 0; 
  }
  to { 
    transform: translateX(0); 
    opacity: 1; 
  }
}
```
Used on: Onboarding steps, messages

### Gradient Animation
```css
@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```
Used on: Background gradients (8s loop)

---

## Glass Morphism Effect

**CSS Implementation:**
```css
.glass {
  background-color: rgb(255 255 255 / 0.1);
  backdrop-filter: blur(24px);
  border: 1px solid rgb(255 255 255 / 0.2);
}
```

**Visual Result:**
- Semi-transparent white background
- Blurred background content shows through
- Subtle white border
- Creates "frosted glass" effect

---

## Responsive Breakpoints

- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 1024px (adjusted spacing)
- **Desktop**: > 1024px (full layout)

**Mobile Adaptations:**
- Sidebar collapses to menu icon
- Cards full-width
- Touch-friendly button sizes (44px min)
- Stacked form layouts
- Optimized font sizes

---

## Icon Usage (Lucide React)

**Authentication:**
- Mail, Lock, User

**Financial:**
- TrendingUp, DollarSign, Target

**UI Actions:**
- Send, Plus, Menu, X, ChevronRight, ChevronLeft

**Chat:**
- Bot, MessageSquare, LogOut, Loader2

**Status:**
- CheckCircle, AlertCircle

---

This showcase demonstrates all the visual components and their usage throughout the Wealth Coach AI application.
