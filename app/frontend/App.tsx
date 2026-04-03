import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/context/AuthContext";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import TeamSelection from "./pages/TeamSelection";
import MyTeam from "./pages/MyTeam";
import MyTeams from "./pages/MyTeams";
import Leaderboard from "./pages/Leaderboard";
import AIAssistant from "./pages/AIAssistant";
import Players from "./pages/Players";
import PlayerProfile from "./pages/PlayerProfile";
import Matches from "./pages/Matches";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/match/:matchId/team-selection" element={<TeamSelection />} />
            <Route path="/match/:matchId/my-team" element={<MyTeam />} />
            <Route path="/my-teams" element={<MyTeams />} />
            <Route path="/leaderboard/season" element={<Leaderboard />} />
            <Route path="/leaderboard/match/:matchId" element={<Leaderboard />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
            <Route path="/players" element={<Players />} />
            <Route path="/players/:playerId" element={<PlayerProfile />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
