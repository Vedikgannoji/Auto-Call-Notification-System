import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext, API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import { Mail, Lock, GraduationCap } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      login(response.data.access_token, response.data.user);
      toast.success('Login successful');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://customer-assets.emergentagent.com/job_3bb85702-731e-4925-a73b-daa0be7005b3/artifacts/wzgy3auo_image.png')`
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center gap-3 mb-6">
            <GraduationCap className="w-12 h-12" />
            <div>
              <h1 className="text-4xl font-bold" style={{ fontFamily: 'Manrope' }}>MLR Institute</h1>
              <p className="text-lg text-slate-200">Auto-Call Notification System</p>
            </div>
          </div>
          <p className="text-slate-200 text-lg leading-relaxed max-w-md">
            Streamline attendance monitoring with automated SMS and voice call notifications to parents.
          </p>
        </div>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gradient-to-br from-blue-50 to-slate-50">
        <Card className="w-full max-w-md shadow-xl border-0">
          <CardContent className="p-8">
            <div className="lg:hidden mb-8 text-center">
              <GraduationCap className="w-16 h-16 mx-auto mb-4 text-[#0F172A]" />
              <h2 className="text-3xl font-bold text-[#0F172A]" style={{ fontFamily: 'Manrope' }}>MLR Institute</h2>
              <p className="text-slate-600">Auto-Call Notification System</p>
            </div>

            <div className="mb-6">
              <h2 className="text-2xl font-bold text-[#0F172A] mb-2" style={{ fontFamily: 'Manrope' }}>Welcome Back</h2>
              <p className="text-slate-600">Sign in to manage attendance notifications</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-[#0F172A] font-medium">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@mlrit.ac.in"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="pl-11 h-12 border-slate-300 focus:border-[#2563EB] focus:ring-[#2563EB]"
                    data-testid="email-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-[#0F172A] font-medium">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="pl-11 h-12 border-slate-300 focus:border-[#2563EB] focus:ring-[#2563EB]"
                    data-testid="password-input"
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-[#2563EB] hover:bg-[#1d4ed8] text-white font-semibold transition-all duration-200"
                disabled={loading}
                data-testid="login-button"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-slate-600">
              <p>Demo: admin@mlrit.ac.in / admin123</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
