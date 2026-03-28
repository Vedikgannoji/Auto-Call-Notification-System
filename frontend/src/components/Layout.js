import React, { useContext, useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Users,
  UserCheck,
  Calendar,
  Bell,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  GraduationCap
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/students', label: 'Students', icon: Users },
    { path: '/parents', label: 'Parents', icon: UserCheck },
    { path: '/attendance', label: 'Attendance', icon: Calendar },
    { path: '/notifications', label: 'Notifications', icon: Bell },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <aside className="hidden md:flex md:w-64 md:flex-col bg-slate-900 text-slate-100 border-r border-slate-800">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <GraduationCap className="w-8 h-8 text-[#2563EB]" />
            <div>
              <h2 className="text-lg font-bold" style={{ fontFamily: 'Manrope' }}>MLR Institute</h2>
              <p className="text-xs text-slate-400">Auto-Call System</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-[#2563EB] text-white font-medium'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`
                }
                data-testid={`nav-${item.label.toLowerCase()}`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="mb-4 p-3 bg-slate-800 rounded-lg">
            <p className="text-sm text-slate-400">Logged in as</p>
            <p className="text-sm font-medium text-white truncate">{user?.email}</p>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-800 border-slate-700"
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-[#2563EB]" />
            <h2 className="text-lg font-bold" style={{ fontFamily: 'Manrope' }}>MLR Institute</h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-button"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>
        </div>

        {mobileMenuOpen && (
          <nav className="mt-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-[#2563EB] text-white font-medium'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full justify-start mt-4"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </Button>
          </nav>
        )}
      </div>

      <main className="flex-1 md:pt-0 pt-20">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
