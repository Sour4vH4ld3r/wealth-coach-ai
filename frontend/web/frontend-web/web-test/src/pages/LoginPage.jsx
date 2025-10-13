import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Lock, Mail, TrendingUp } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify({ email }));

      // Check onboarding status from backend
      try {
        const onboardingResponse = await fetch(`${API_BASE_URL}/api/v1/onboarding/status`, {
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
        });

        if (onboardingResponse.ok) {
          const onboardingData = await onboardingResponse.json();
          if (onboardingData.onboarding_completed) {
            navigate('/chat');
          } else {
            navigate('/onboarding');
          }
        } else {
          // If status check fails, assume onboarding needed
          navigate('/onboarding');
        }
      } catch (onboardingError) {
        console.error('Failed to check onboarding status:', onboardingError);
        // If error, assume onboarding needed
        navigate('/onboarding');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 gradient-finance animate-gradient overflow-hidden">
      <div className="absolute inset-0 bg-black/30"></div>

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="w-full max-w-md relative z-10 animate-fade-in">
        <div className="text-center mb-6 sm:mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-white/10 backdrop-blur-xl mb-4 animate-float glow">
            <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-2 text-shadow">Wealth Coach AI</h1>
          <p className="text-sm sm:text-base text-white/80">Your Personal Financial Assistant</p>
        </div>

        <Card className="animate-slide-up glass border-white/20">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl sm:text-2xl">Welcome Back</CardTitle>
            <CardDescription className="text-xs sm:text-sm">Sign in to continue your financial journey</CardDescription>
          </CardHeader>
          <form onSubmit={handleLogin}>
            <CardContent className="space-y-4 sm:space-y-5">
              {error && (
                <div className="p-3 sm:p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs sm:text-sm backdrop-blur-sm animate-slide-in">
                  <div className="flex items-start gap-2">
                    <span className="text-red-400 mt-0.5">⚠</span>
                    <span>{error}</span>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-xs sm:text-sm">Email</Label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-white/50 group-focus-within:text-primary-400 transition-colors" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 sm:pl-11 text-sm sm:text-base"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-xs sm:text-sm">Password</Label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-white/50 group-focus-within:text-primary-400 transition-colors" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 sm:pl-11 text-sm sm:text-base"
                    required
                  />
                </div>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4 pt-2">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>

              <div className="text-center text-xs sm:text-sm text-white/70">
                Don't have an account?{' '}
                <Link to="/register" className="text-primary-300 hover:text-primary-200 font-medium underline-offset-4 hover:underline transition-all">
                  Sign up
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>

        <div className="mt-6 sm:mt-8 text-center text-white/60 text-xs sm:text-sm">
          <p className="flex items-center justify-center gap-2">
            <Lock className="w-3 h-3 sm:w-4 sm:h-4" />
            Secure, private, and intelligent financial guidance
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
