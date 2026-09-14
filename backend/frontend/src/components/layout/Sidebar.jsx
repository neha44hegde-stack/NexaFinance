import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Receipt, 
  Wallet, 
  PiggyBank, 
  BarChart3, 
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const { logout, user } = useAuth();

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/transactions', icon: Receipt, label: 'Transactions' },
    { path: '/budgets', icon: Wallet, label: 'Budgets' },
    { path: '/savings', icon: PiggyBank, label: 'Savings' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className={`bg-primary-green text-white flex flex-col transition-all duration-300 ${
      isOpen ? 'w-64' : 'w-20'
    }`}>
      <div className="p-6 flex items-center justify-between border-b border-white/10">
        <div className={`flex items-center gap-2 ${!isOpen && 'justify-center w-full'}`}>
          <span className="text-2xl">💰</span>
          {isOpen && (
            <span className="font-serif text-xl font-bold">Sensible</span>
          )}
        </div>
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded hover:bg-white/10 transition-colors"
        >
          {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      <div className="flex-1 p-4">
        {isOpen && (
          <div className="text-xs uppercase tracking-wider text-white/50 mb-4 px-3">
            Your Money
          </div>
        )}
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-white/20 text-white' 
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                } ${!isOpen && 'justify-center'}`
              }
            >
              <item.icon size={20} />
              {isOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-white/10">
        <button
          onClick={logout}
          className={`flex items-center gap-3 px-3 py-3 rounded-lg text-white/70 hover:bg-white/10 hover:text-white transition-colors w-full ${
            !isOpen && 'justify-center'
          }`}
        >
          <LogOut size={20} />
          {isOpen && <span>Logout</span>}
        </button>
        {isOpen && user && (
          <div className="mt-4 px-3 text-sm text-white/50">
            {user.username}
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;