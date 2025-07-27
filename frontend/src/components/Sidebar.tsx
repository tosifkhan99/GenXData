import { Link } from 'react-router-dom';
import { Home, Settings, Github, Mail, Briefcase, Sun, Moon, ChevronLeft, ChevronRight } from 'lucide-react';
import { useTheme } from '../contexts/ThemeProvider';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

const Sidebar = () => {
  const { theme, setTheme } = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <aside
      className={`h-screen flex flex-col justify-between bg-muted/40 border-r transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      <div className="p-4">
        <div className="flex items-center justify-between mb-6">
          {!isCollapsed && <h2 className="text-xl font-semibold tracking-tight">GenXData</h2>}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="ml-auto"
          >
            {isCollapsed ? <ChevronRight className="h-6 w-6" /> : <ChevronLeft className="h-6 w-6" />}
          </Button>
        </div>
        <nav className="space-y-2">
          <Link
            to="/"
            className={`flex items-center px-3 py-3 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title="Home"
          >
            <Home className={`${isCollapsed ? 'h-7 w-7' : 'h-5 w-5'}`} />
            {!isCollapsed && <span className="ml-2">Home</span>}
          </Link>
          <Link
            to="/generator"
            className={`flex items-center px-3 py-3 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title="Generator"
          >
            <Settings className={`${isCollapsed ? 'h-7 w-7' : 'h-5 w-5'}`} />
            {!isCollapsed && <span className="ml-2">Generator</span>}
          </Link>
        </nav>
      </div>

      <div className="p-4">
        <Button
          variant="outline"
          size="icon"
          onClick={toggleTheme}
          className={`mb-4 ${isCollapsed ? 'w-full' : 'w-full'}`}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ?
            <Sun className={`${isCollapsed ? 'h-7 w-7' : 'h-[1.2rem] w-[1.2rem]'}`} /> :
            <Moon className={`${isCollapsed ? 'h-7 w-7' : 'h-[1.2rem] w-[1.2rem]'}`} />
          }
          {!isCollapsed && <span className="ml-2">Toggle Theme</span>}
        </Button>

        <nav className="space-y-2 border-t pt-4 mt-4">
          <a
            href="https://github.com/tosifkhan99/GenXData"
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center px-3 py-3 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title="GitHub Project"
          >
            <Github className={`${isCollapsed ? 'h-7 w-7' : 'h-5 w-5'}`} />
            {!isCollapsed && <span className="ml-2">GitHub Project</span>}
          </a>
          <a
            href="mailto:khantosif94@gmail.com"
            className={`flex items-center px-3 py-3 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title="Email Me"
          >
            <Mail className={`${isCollapsed ? 'h-7 w-7' : 'h-5 w-5'}`} />
            {!isCollapsed && <span className="ml-2">Email Me</span>}
          </a>
          <a
            href="https://tosif-khan-vercel.com"
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center px-3 py-3 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title="My Website"
          >
            <Briefcase className={`${isCollapsed ? 'h-7 w-7' : 'h-5 w-5'}`} />
            {!isCollapsed && <span className="ml-2">My Website</span>}
          </a>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
