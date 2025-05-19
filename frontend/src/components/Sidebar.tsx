import { Link } from 'react-router-dom';
import { Home, Settings, Github, Mail, Briefcase, Sun, Moon} from 'lucide-react';
import { useTheme } from '../contexts/ThemeProvider';
import { Button } from '@/components/ui/button'; // Assuming shadcn/ui button is available

const Sidebar = () => {
  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <aside className="w-64 h-screen p-4 flex flex-col justify-between bg-muted/40 border-r">
      <div>
        <div className="mb-6">
          <h2 className="text-xl font-semibold tracking-tight px-3">GenXData</h2>
        </div>
        <nav className="space-y-1">
          <Link
            to="/"
            className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground"
          >
            <Home className="w-5 h-5 mr-2" />
            Home
          </Link>
          <Link
            to="/generator"
            className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground"
          >
            <Settings className="w-5 h-5 mr-2" />
            Generator
          </Link>
          
          
        </nav>
      </div>

      <div>
        <Button 
          variant="outline" 
          size="icon" 
          onClick={toggleTheme} 
          className="mb-4 w-full"
        >
          {theme === 'dark' ? <Sun className="h-[1.2rem] w-[1.2rem]" /> : <Moon className="h-[1.2rem] w-[1.2rem]" />}
          <span className="sr-only">Toggle theme</span>
        </Button>

        <nav className="space-y-1 border-t pt-4 mt-4">
          <a
            href="https://github.com/tosifkhan99/GenXData"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground"
          >
            <Github className="w-5 h-5 mr-2" />
            GitHub Project
          </a>
          <a
            href="mailto:khantosif94@gmail.com"
            className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground"
          >
            <Mail className="w-5 h-5 mr-2" />
            Email Me
          </a>
          <a
            href="https://tosif-khan-vercel.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-accent-foreground"
          >
            <Briefcase className="w-5 h-5 mr-2" />
            My Website
          </a>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar; 