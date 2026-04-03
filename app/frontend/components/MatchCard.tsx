import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, MapPin } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { getTeamLogo, handleLogoError } from "@/lib/team-utils";

interface Match {
  match_id: number;
  match_number?: number;
  match_date: string;
  match_time?: string;
  team_home: string;
  team_away: string;
  venue: string;
  status: string;
  winner?: string;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  live: { label: "🔴 LIVE", className: "text-destructive pulse-live font-bold" },
  upcoming: { label: "Upcoming", className: "text-warning font-medium" },
  completed: { label: "Completed", className: "text-muted-foreground" },
};

export const MatchCard = ({ match }: { match: Match }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const s = statusConfig[match.status] || statusConfig.upcoming;

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          {match.match_number && <span className="text-xs text-muted-foreground">Match #{match.match_number}</span>}
          <span className={`text-xs ${s.className}`}>{s.label}</span>
        </div>
        <div className="flex items-center justify-between mb-3 gap-2">
          <div className="flex-1 flex flex-col items-center gap-2">
            {getTeamLogo(match.team_home) && (
              <img 
                src={getTeamLogo(match.team_home)} 
                alt={match.team_home}
                className="h-10 w-10 object-contain"
                onError={handleLogoError}
              />
            )}
            <span className="font-bold text-sm text-center">{match.team_home}</span>
          </div>
          <span className="text-xs text-muted-foreground px-2">vs</span>
          <div className="flex-1 flex flex-col items-center gap-2">
            {getTeamLogo(match.team_away) && (
              <img 
                src={getTeamLogo(match.team_away)} 
                alt={match.team_away}
                className="h-10 w-10 object-contain"
                onError={handleLogoError}
              />
            )}
            <span className="font-bold text-sm text-center">{match.team_away}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
          <Calendar className="h-3 w-3" /> {match.match_date} {match.match_time && `• ${match.match_time}`}
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
          <MapPin className="h-3 w-3" /> {match.venue}
        </div>
        {match.winner && <p className="text-xs font-medium text-primary mb-2">🏆 {match.winner}</p>}
        {match.status === "upcoming" && isAuthenticated && (
          <Button size="sm" className="w-full mt-1" onClick={() => navigate(`/match/${match.match_id}/team-selection`)}>
            Create Team
          </Button>
        )}
      </CardContent>
    </Card>
  );
};
