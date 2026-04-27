import { Link, useNavigate } from 'react-router-dom';
import {
  AcademicCapIcon,
  ArrowRightOnRectangleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  HomeIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="sticky top-0 z-50 w-full glass border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex flex-shrink-0 items-center gap-2 group">
              <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                <AcademicCapIcon className="h-6 w-6 text-primary" />
              </div>
              <span className="font-heading font-bold text-xl tracking-tight">
                AI Intern<span className="text-primary">Match</span>
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
  );
}
