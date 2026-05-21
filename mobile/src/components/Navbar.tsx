import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  AcademicCapIcon,
  ArrowRightOnRectangleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  HomeIcon,
  UserCircleIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* =========================================================================
          DESKTOP & TABLET NAVIGATION (Visible on screens larger than sm)
          ========================================================================= */}
      <nav className="hidden sm:block sticky top-0 z-50 w-full glass border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex flex-shrink-0 items-center gap-2 group">
                <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                  <AcademicCapIcon className="h-6 w-6 text-primary" />
                </div>
                <span className="font-heading font-bold text-xl tracking-tight">
                  StageMatch <span className="text-primary">AI</span>
                </span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <Link to="/offers" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                <DocumentTextIcon className="h-5 w-5" />
                <span>Offres</span>
              </Link>

              {user ? (
                <>
                  <Link to="/dashboard" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                    <HomeIcon className="h-5 w-5" />
                    <span>{user.role === 'company' ? 'Accueil' : 'Dashboard'}</span>
                  </Link>
                  {user.role === 'company' ? (
                    <Link to="/company/offers" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                      <DocumentTextIcon className="h-5 w-5" />
                      <span>Mes offres</span>
                    </Link>
                  ) : null}
                  <Link to="/profile" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                    <UserCircleIcon className="h-5 w-5" />
                    <span>Profil</span>
                  </Link>
                  <Link to="/market-trends" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                    <ChartBarIcon className="h-5 w-5" />
                    <span>Tendances</span>
                  </Link>
                  {user.role === 'admin' && (
                    <Link to="/admin" className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1 font-medium">
                      <ShieldCheckIcon className="h-5 w-5" />
                      <span>Admin</span>
                    </Link>
                  )}
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-1 text-red-500 hover:text-red-600 transition-colors px-3 py-2 rounded-md hover:bg-red-50/50 font-medium"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5" />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  className="bg-primary text-white hover:bg-primary/90 transition-all px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg font-medium text-sm"
                >
                  Se Connecter
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* =========================================================================
          MOBILE HEADER (Sticky top bar for app brand + logout on mobile viewports)
          ========================================================================= */}
      <header className="sm:hidden sticky top-0 z-50 w-full glass-dark border-b border-border/80 px-4 py-3 flex justify-between items-center h-14">
        <Link to="/" className="flex items-center gap-2">
          <AcademicCapIcon className="h-6 w-6 text-primary animate-pulse" />
          <span className="font-heading font-bold text-lg tracking-tight">
            StageMatch <span className="text-primary">AI</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-2">
            {user.role === 'admin' && (
              <Link to="/admin" className="p-1.5 text-secondary-foreground hover:text-primary transition-colors">
                <ShieldCheckIcon className="h-5 w-5" />
              </Link>
            )}
            <button
              onClick={handleLogout}
              className="p-1.5 text-red-500 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50/50"
              aria-label="Logout"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        )}
      </header>

      {/* =========================================================================
          MOBILE BOTTOM NAVIGATION TAB BAR (Sticky bottom bar on mobile viewports)
          ========================================================================= */}
      <nav className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-background/95 border-t border-border/80 backdrop-blur-md pb-safe">
        <div className="flex justify-around items-center h-16 px-2">
          {/* 1. Offers / Explore Tab */}
          <Link
            to="/offers"
            className={`flex flex-col items-center justify-center flex-1 h-full py-1.5 transition-all duration-200 ${
              isActive('/offers') ? 'text-primary scale-105' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <DocumentTextIcon className="h-5 w-5" />
            <span className="text-[10px] mt-1 font-medium">Offres</span>
          </Link>

          {/* 2. Dashboard / Home Tab */}
          <Link
            to={user ? '/dashboard' : '/login'}
            className={`flex flex-col items-center justify-center flex-1 h-full py-1.5 transition-all duration-200 ${
              isActive('/dashboard') || isActive('/') ? 'text-primary scale-105' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <HomeIcon className="h-5 w-5" />
            <span className="text-[10px] mt-1 font-medium">
              {user && user.role === 'company' ? 'Accueil' : 'Dashboard'}
            </span>
          </Link>

          {/* 3. Trends Tab */}
          {user && (
            <Link
              to="/market-trends"
              className={`flex flex-col items-center justify-center flex-1 h-full py-1.5 transition-all duration-200 ${
                isActive('/market-trends') ? 'text-primary scale-105' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <ChartBarIcon className="h-5 w-5" />
              <span className="text-[10px] mt-1 font-medium">Tendances</span>
            </Link>
          )}

          {/* 4. Profile Tab */}
          <Link
            to={user ? '/profile' : '/login'}
            className={`flex flex-col items-center justify-center flex-1 h-full py-1.5 transition-all duration-200 ${
              isActive('/profile') || isActive('/login') || isActive('/register')
                ? 'text-primary scale-105'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <UserCircleIcon className="h-5 w-5" />
            <span className="text-[10px] mt-1 font-medium">
              {user ? 'Profil' : 'Connexion'}
            </span>
          </Link>
        </div>
      </nav>
    </>
  );
}
