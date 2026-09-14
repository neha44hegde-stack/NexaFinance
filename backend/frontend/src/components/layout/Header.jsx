import React from 'react';
import { Menu, Bell, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Header = ({ toggleSidebar }) => {
  const { user } = useAuth();

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Menu size={24} />
          </button>
          <div>
            <h1 className="font-serif text-xl font-semibold text-primary-green">
              {user?.name ? `Good ${new Date().getHours() < 12 ? 'morning' : 'afternoon'}, ${user.name}` : 'Dashboard'}
            </h1>
            <p className="text-sm text-gray-500">
              {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <User size={20} />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;