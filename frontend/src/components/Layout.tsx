/** Main layout component with navigation. */

import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu, X, ChevronDown } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import type { Language } from '../i18n/translations';

const languages: { code: Language; name: string; flag: string }[] = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'pl', name: 'Polski', flag: '🇵🇱' },
  { code: 'ro', name: 'Română', flag: '🇷🇴' },
];

const Layout = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);
  const { t, language, setLanguage } = useLanguage();

  const navItems = [
    { path: '/chat', label: t.chat },
    { path: '/upload', label: t.upload },
    { path: '/documents', label: t.documents },
    { path: '/analytics', label: t.analytics },
  ];

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Clean, professional header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            
            {/* Logo and Brand */}
            <Link 
              to="/" 
              className="flex items-center gap-3 flex-shrink-0 group"
            >
              <img 
                src="/CWK.L_BIG.png" 
                alt="Cranswick" 
                className="h-7 sm:h-8 object-contain"
              />
              <div className="hidden sm:block h-6 w-px bg-slate-200" />
              <span className="hidden sm:block text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
                Technical Standards Agent
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center">
              <div className="flex items-center bg-slate-100 rounded-lg p-1">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150 ${
                        isActive
                          ? 'bg-white text-slate-900 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>

              {/* Language Selector - Minimal */}
              <div className="relative ml-4">
                <button
                  onClick={() => setLanguageMenuOpen(!languageMenuOpen)}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                  aria-label="Select language"
                >
                  <span className="text-base">{currentLanguage.flag}</span>
                  <ChevronDown size={14} className={`transition-transform ${languageMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {languageMenuOpen && (
                  <>
                    <div 
                      className="fixed inset-0 z-10" 
                      onClick={() => setLanguageMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-20">
                      {languages.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => {
                            setLanguage(lang.code);
                            setLanguageMenuOpen(false);
                          }}
                          className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2.5 hover:bg-slate-50 transition-colors ${
                            language === lang.code ? 'text-blue-600 font-medium bg-blue-50' : 'text-slate-700'
                          }`}
                        >
                          <span>{lang.flag}</span>
                          <span>{lang.name}</span>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </nav>

            {/* Mobile Controls */}
            <div className="md:hidden flex items-center gap-1">
              {/* Mobile Language */}
              <button
                onClick={() => {
                  setLanguageMenuOpen(!languageMenuOpen);
                  setMobileMenuOpen(false);
                }}
                className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
                aria-label="Select language"
              >
                <span className="text-lg">{currentLanguage.flag}</span>
              </button>
              
              {/* Mobile Menu Toggle */}
              <button
                onClick={() => {
                  setMobileMenuOpen(!mobileMenuOpen);
                  setLanguageMenuOpen(false);
                }}
                className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 bg-white">
            <div className="px-4 py-3 space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        )}

        {/* Mobile Language Dropdown */}
        {languageMenuOpen && (
          <div className="md:hidden border-t border-slate-200 bg-white">
            <div className="px-4 py-3 space-y-1">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setLanguage(lang.code);
                    setLanguageMenuOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-sm flex items-center gap-3 transition-colors ${
                    language === lang.code
                      ? 'bg-blue-50 text-blue-700 font-medium'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
