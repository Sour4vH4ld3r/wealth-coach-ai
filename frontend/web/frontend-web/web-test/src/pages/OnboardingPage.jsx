import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Target, TrendingUp, IndianRupee, ChevronRight, ChevronLeft, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

const OnboardingPage = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    financial_goals: '',
    risk_tolerance: 'moderate',
    income_range: '',
    occupation: '',
  });
  const navigate = useNavigate();

  const totalSteps = 3;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          financial_goals: formData.financial_goals,
          risk_tolerance: formData.risk_tolerance,
          income_range: formData.income_range,
          occupation: formData.occupation,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Onboarding failed');
      }

      // Onboarding status is now tracked in the backend database
      navigate('/chat');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4 animate-slide-in">
            <div className="flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-primary-500/20 mx-auto mb-4 glow">
              <Target className="w-7 h-7 sm:w-8 sm:h-8 text-primary-400" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="financial_goals" className="text-sm sm:text-base">What are your financial goals?</Label>
              <textarea
                id="financial_goals"
                name="financial_goals"
                rows={4}
                className="flex w-full rounded-lg border border-white/20 bg-white/5 backdrop-blur-sm px-3 sm:px-4 py-2 text-sm sm:text-base text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500/50 focus:bg-white/10 transition-all duration-300 hover:border-white/30 resize-none shadow-sm hover:shadow-md focus:shadow-lg"
                placeholder="E.g., Save for retirement, buy a house, pay off debt, build emergency fund..."
                value={formData.financial_goals}
                onChange={handleChange}
                required
              />
              <p className="text-xs sm:text-sm text-white/60 flex items-start gap-1.5">
                <span className="mt-0.5">💡</span>
                <span>Share your short-term and long-term financial aspirations</span>
              </p>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4 animate-slide-in">
            <div className="flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-accent-500/20 mx-auto mb-4 glow">
              <TrendingUp className="w-7 h-7 sm:w-8 sm:h-8 text-accent-400" />
            </div>
            <div className="space-y-2">
              <Label className="text-sm sm:text-base">What's your risk tolerance?</Label>
              <div className="space-y-2 sm:space-y-3">
                {['conservative', 'moderate', 'aggressive'].map((risk) => (
                  <label
                    key={risk}
                    className={`flex items-start p-3 sm:p-4 rounded-lg border cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
                      formData.risk_tolerance === risk
                        ? 'border-primary-500/50 bg-primary-500/10 shadow-lg shadow-primary-500/20'
                        : 'border-white/20 bg-white/5 hover:bg-white/10 hover:border-white/30'
                    }`}
                  >
                    <input
                      type="radio"
                      name="risk_tolerance"
                      value={risk}
                      checked={formData.risk_tolerance === risk}
                      onChange={handleChange}
                      className="w-4 h-4 sm:w-5 sm:h-5 text-primary-600 focus:ring-primary-500 focus:ring-offset-0 mt-0.5"
                    />
                    <div className="ml-3 flex-1">
                      <div className="text-white font-medium capitalize text-sm sm:text-base">{risk}</div>
                      <div className="text-xs sm:text-sm text-white/60 mt-0.5">
                        {risk === 'conservative' && 'Prefer safety and stability over high returns'}
                        {risk === 'moderate' && 'Balanced approach with moderate growth potential'}
                        {risk === 'aggressive' && 'Comfortable with higher risk for potential gains'}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4 animate-slide-in">
            <div className="flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-green-500/20 mx-auto mb-4 glow">
              <IndianRupee className="w-7 h-7 sm:w-8 sm:h-8 text-green-400" />
            </div>
            <div className="space-y-3 sm:space-y-4">
              <div className="space-y-2">
                <Label htmlFor="occupation" className="text-sm sm:text-base">Occupation</Label>
                <Input
                  id="occupation"
                  name="occupation"
                  type="text"
                  placeholder="e.g., Software Engineer, Teacher, Business Owner"
                  value={formData.occupation}
                  onChange={handleChange}
                  className="text-sm sm:text-base"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="income_range" className="text-sm sm:text-base">Annual Income Range</Label>
                <select
                  id="income_range"
                  name="income_range"
                  value={formData.income_range}
                  onChange={handleChange}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"
                  required
                >
                  <option value="">Select income range</option>
                  <option value="₹0-₹3L">₹0 - ₹3 Lakhs</option>
                  <option value="₹3L-₹6L">₹3 - ₹6 Lakhs</option>
                  <option value="₹6L-₹10L">₹6 - ₹10 Lakhs</option>
                  <option value="₹10L-₹15L">₹10 - ₹15 Lakhs</option>
                  <option value="₹15L-₹25L">₹15 - ₹25 Lakhs</option>
                  <option value="₹25L+">₹25 Lakhs+</option>
                </select>
              </div>

              <div className="p-3 sm:p-4 rounded-lg bg-gradient-to-r from-primary-500/10 to-purple-500/10 border border-primary-500/30 backdrop-blur-sm">
                <div className="text-xs sm:text-sm text-white/70 mb-1 flex items-center gap-1.5">
                  <span>💡</span>
                  <span>Why we ask</span>
                </div>
                <div className="text-xs sm:text-sm text-white/80">
                  Your occupation and income help us provide personalized financial advice tailored to your situation
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 gradient-finance animate-gradient overflow-hidden">
      <div className="absolute inset-0 bg-black/30"></div>

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-10 left-10 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="w-full max-w-2xl relative z-10 animate-fade-in">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-2 text-shadow">Let's Get Started</h1>
          <p className="text-sm sm:text-base text-white/80">Help us personalize your financial coaching experience</p>
        </div>

        <div className="mb-6 px-4 sm:px-8">
          <div className="relative">
            <div className="flex items-center justify-between mb-3">
              {[...Array(totalSteps)].map((_, i) => (
                <div key={i} className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center font-semibold text-sm sm:text-base transition-all duration-500 ${
                      i + 1 < step
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/50'
                        : i + 1 === step
                        ? 'bg-gradient-to-r from-primary-500 to-purple-600 text-white shadow-lg shadow-primary-500/50 glow'
                        : 'bg-white/10 text-white/50 backdrop-blur-sm'
                    }`}
                  >
                    {i + 1 < step ? <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6" /> : i + 1}
                  </div>
                  <div className={`mt-2 text-xs sm:text-sm font-medium transition-all duration-300 ${
                    i + 1 <= step ? 'text-white' : 'text-white/50'
                  }`}>
                    {i === 0 && 'Goals'}
                    {i === 1 && 'Risk'}
                    {i === 2 && 'Profile'}
                  </div>
                </div>
              ))}
            </div>
            <div className="absolute top-5 sm:top-6 left-0 right-0 h-1 bg-white/10 -z-10 mx-5 sm:mx-6">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-purple-600 transition-all duration-500"
                style={{ width: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        <Card className="animate-slide-up glass border-white/20">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between mb-2">
              <CardTitle className="text-xl sm:text-2xl">Step {step} of {totalSteps}</CardTitle>
              <div className="text-xs sm:text-sm font-medium text-primary-400 bg-primary-500/10 px-3 py-1 rounded-full border border-primary-500/20">
                {Math.round((step / totalSteps) * 100)}% Complete
              </div>
            </div>
            <CardDescription className="text-xs sm:text-sm">
              {step === 1 && 'Tell us about your financial aspirations'}
              {step === 2 && 'Help us understand your investment preferences'}
              {step === 3 && 'Share your professional background'}
            </CardDescription>
          </CardHeader>

          <form onSubmit={step === totalSteps ? handleSubmit : (e) => { e.preventDefault(); handleNext(); }}>
            <CardContent className="min-h-[280px] sm:min-h-[320px]">
              {error && (
                <div className="mb-4 p-3 sm:p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs sm:text-sm backdrop-blur-sm animate-slide-in">
                  <div className="flex items-start gap-2">
                    <span className="text-red-400 mt-0.5">⚠</span>
                    <span>{error}</span>
                  </div>
                </div>
              )}
              {renderStep()}
            </CardContent>

            <CardFooter className="flex justify-between pt-4 border-t border-white/10">
              {step > 1 ? (
                <Button type="button" variant="outline" onClick={handleBack} size="default">
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              ) : (
                <div></div>
              )}

              {step < totalSteps ? (
                <Button type="submit" size="default" variant="default">
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button type="submit" disabled={loading} size="default" variant="default">
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                      Completing...
                    </>
                  ) : (
                    <>
                      Complete
                      <CheckCircle className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              )}
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default OnboardingPage;
