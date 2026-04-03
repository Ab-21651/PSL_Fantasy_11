import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Menu, X, User, LogOut, LayoutDashboard, Trophy, Bot, Users, Calendar, Shirt } from "lucide-react";
import { useState } from "react";

const navLinks = [
  { to: "/matches", label: "Matches", icon: Calendar },
  { to: "/players", label: "Players", icon: Users },
  { to: "/my-teams", label: "My Teams", icon: Shirt },
  { to: "/leaderboard/season", label: "Leaderboard", icon: Trophy },
];

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-border/50 bg-card/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-extrabold text-xl tracking-tight">
          <span className="text-2xl">🏏</span>
          <span>Cric<span className="text-primary">Mind</span></span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground rounded-md hover:bg-muted transition-colors"
            >
              {l.label}
            </Link>
          ))}
          {isAuthenticated && (
            <Link
              to="/ai-assistant"
              className="px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground rounded-md hover:bg-muted transition-colors"
            >
              AI Assistant
            </Link>
          )}
        </div>

        <div className="hidden md:flex items-center gap-2">
          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <User className="h-4 w-4" />
                  {user?.username}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                  <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" /> Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button variant="ghost" size="sm" onClick={() => navigate("/login")}>Login</Button>
              <Button size="sm" onClick={() => navigate("/register")}>Join Now</Button>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-card p-4 space-y-2 animate-slide-up">
          {navLinks.map((l) => (
            <Link key={l.to} to={l.to} onClick={() => setMobileOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-muted">
              <l.icon className="h-4 w-4" /> {l.label}
            </Link>
          ))}
          {isAuthenticated && (
            <>
              <Link to="/ai-assistant" onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-muted">
                <Bot className="h-4 w-4" /> AI Assistant
              </Link>
              <Link to="/dashboard" onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-muted">
                <LayoutDashboard className="h-4 w-4" /> Dashboard
              </Link>
              <button onClick={() => { handleLogout(); setMobileOpen(false); }}
                className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-muted w-full text-left text-destructive">
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </>
          )}
          {!isAuthenticated && (
            <div className="flex gap-2 pt-2">
              <Button variant="ghost" size="sm" className="flex-1" onClick={() => { navigate("/login"); setMobileOpen(false); }}>Login</Button>
              <Button size="sm" className="flex-1" onClick={() => { navigate("/register"); setMobileOpen(false); }}>Join Now</Button>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
