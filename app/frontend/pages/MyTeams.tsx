import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { Loader2, Trophy, Calendar, Users } from "lucide-react";
import { getTeamLogo } from "@/lib/team-utils";

interface MyTeamData {
  team_id: string;
  match_id: string;
  team_name: string;
  credits_used: number;
  total_points: number;
  team_home: string;
  team_away: string;
  match_date: string;
  status: string;
}

export default function MyTeams() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const { data: teams, isLoading, error } = useQuery<MyTeamData[]>({
    queryKey: ["my-teams"],
    queryFn: async () => {
      try {
        const response = await api.get<MyTeamData[]>("/fantasy/my-teams");
        console.log("Teams response:", response);
        return response || [];
      } catch (err) {
        console.error("Error fetching teams:", err);
        return [];
      }
    },
    enabled: !!isAuthenticated,
  });

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
        <Navbar />
        <div className="container py-12 text-center">
          <h1 className="text-2xl font-bold mb-4">Please login to view your teams</h1>
          <Button onClick={() => navigate("/login")}>Login</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <Navbar />
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">My Teams</h1>
          <p className="text-muted-foreground">View and manage all your fantasy teams</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : !teams || teams.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No teams yet</h3>
              <p className="text-muted-foreground mb-4">
                You haven't created any fantasy teams yet. Check out the upcoming matches!
              </p>
              <Button onClick={() => navigate("/matches")}>View Matches</Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {teams.map((team) => (
              <Card
                key={team.team_id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/match/${team.match_id}/my-team`)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{team.team_name}</CardTitle>
                    <Badge variant={team.status === "completed" ? "default" : "secondary"}>
                      {team.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Match Info */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 flex-1">
                        <img
                          src={getTeamLogo(team.team_home)}
                          alt={team.team_home}
                          className="h-8 w-8 object-contain"
                        />
                        <span className="text-sm font-medium truncate">{team.team_home}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">vs</span>
                      <div className="flex items-center gap-2 flex-1 justify-end">
                        <span className="text-sm font-medium truncate">{team.team_away}</span>
                        <img
                          src={getTeamLogo(team.team_away)}
                          alt={team.team_away}
                          className="h-8 w-8 object-contain"
                        />
                      </div>
                    </div>

                    {/* Date */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      {new Date(team.match_date).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center justify-between pt-2 border-t">
                      <div className="text-center flex-1">
                        <div className="text-xs text-muted-foreground">Credits Used</div>
                        <div className="text-lg font-bold">{team.credits_used}</div>
                      </div>
                      <div className="text-center flex-1 border-l">
                        <div className="text-xs text-muted-foreground">Points</div>
                        <div className="text-lg font-bold flex items-center justify-center gap-1">
                          <Trophy className="h-4 w-4 text-yellow-500" />
                          {team.total_points}
                        </div>
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/match/${team.match_id}/my-team`);
                      }}
                    >
                      View Team Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
