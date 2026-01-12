/** Main layout component with navigation. */

import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

const Layout = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { t } = useLanguage();

  const navItems = [
    { path: '/chat', label: t.chat },
    { path: '/documents', label: t.documents },
    { path: '/documents/upload', label: t.upload },
    { path: '/generate', label: t.generate },
    { path: '/analytics', label: t.analytics },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20 sm:h-24">
            {/* Logo and Title */}
            <Link to="/" className="flex flex-col items-start justify-center flex-shrink-0 py-2">
              <img 
                src="/CWK.L_BIG.png" 
                alt="Cranswick Logo" 
                className="h-10 sm:h-12 object-contain mb-1"
              />
              <span className="text-xs sm:text-sm font-semibold text-gray-900">
                DocumentIQ
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex space-x-2 lg:space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-2 lg:px-3 py-2 rounded-md text-xs lg:text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-700 hover:bg-gray-100 rounded-md"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 border-t border-gray-200 mt-2 pt-4">
              <div className="flex flex-col space-y-2">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      location.pathname === item.path
                        ? 'bg-blue-100 text-blue-900'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </nav>
      <main className="container mx-auto px-4 sm:px-6 py-4 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
