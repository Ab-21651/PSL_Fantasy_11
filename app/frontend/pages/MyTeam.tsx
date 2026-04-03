import { useParams } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Crown, Star } from "lucide-react";
import { getTeamLogo, handleLogoError } from "@/lib/team-utils";

const MyTeam = () => {
  const { matchId } = useParams();
  const { data: team, isLoading } = useQuery({
    queryKey: ["my-team", matchId],
    queryFn: () => api.get<any>(`/fantasy/matchday/team/${matchId}`),
  });

  return (
    <ProtectedRoute>
      <Layout>
        <div className="container py-8 max-w-2xl">
          {isLoading ? <Skeleton className="h-96" /> : !team ? (
            <Card><CardContent className="p-8 text-center text-muted-foreground">No team created for this match</CardContent></Card>
          ) : (
            <>
              <div className="gradient-stadium rounded-2xl p-6 text-stadium-foreground text-center mb-6">
                <h1 className="text-2xl font-black">{team.team_name}</h1>
                <div className="flex justify-center gap-4 mt-2 text-sm text-stadium-foreground/70">
                  <span>Credits: {team.credits_used}/100</span>
                  <span>Points: {team.total_points ?? "—"}</span>
                </div>
              </div>

              <div className="space-y-3">
                {team.players?.map((p: any) => (
                  <Card key={p.player_name}>
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {p.is_captain && <Crown className="h-5 w-5 text-secondary" />}
                        {p.is_vice_captain && <Star className="h-5 w-5 text-accent" />}
                        <div>
                          <p className="font-semibold">{p.player_name}</p>
                          <div className="flex items-center gap-1.5 mt-0.5">
                            {getTeamLogo(p.team) && (
                              <img 
                                src={getTeamLogo(p.team)} 
                                alt={p.team}
                                className="h-3 w-3 object-contain"
                                onError={handleLogoError}
                              />
                            )}
                            <p className="text-xs text-muted-foreground">{p.role} • {p.team}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{p.credits}c</Badge>
                        {p.points_earned != null && <Badge>{p.points_earned} pts</Badge>}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default MyTeam;
