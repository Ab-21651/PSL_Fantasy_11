import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { Crown, Star, X, Search, Filter } from "lucide-react";
import { getTeamLogo, handleLogoError } from "@/lib/team-utils";

interface Player {
  player_id: number;
  player_name: string;
  role: string;
  credits: number;
  team?: string;
}

const BUDGET = 100;
const MAX_PLAYERS = 11;
const MAX_PER_TEAM = 9;

const roleBadgeColor: Record<string, string> = {
  Batsman: "bg-accent/10 text-accent",
  Bowler: "bg-primary/10 text-primary",
  "All-rounder": "bg-secondary/10 text-secondary",
  "Wicket-Keeper": "bg-destructive/10 text-destructive",
};

const TeamSelection = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [selected, setSelected] = useState<Player[]>([]);
  const [captainId, setCaptainId] = useState<number | null>(null);
  const [vcId, setVcId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [teamName, setTeamName] = useState("");
  const [showSubmit, setShowSubmit] = useState(false);

  const { data: matchData, isLoading } = useQuery({
    queryKey: ["match", matchId],
    queryFn: () => api.get<any>(`/matches/${matchId}`),
  });

  const createTeamMutation = useMutation({
    mutationFn: (body: any) => api.post("/fantasy/matchday/team", body),
    onSuccess: () => {
      toast({ title: "Team created! 🎉" });
      navigate(`/match/${matchId}/my-team`);
    },
    onError: (err: any) => toast({ title: "Error", description: err.message, variant: "destructive" }),
  });

  const creditsUsed = selected.reduce((s, p) => s + p.credits, 0);
  const remaining = BUDGET - creditsUsed;

  const teamCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    selected.forEach((p) => { counts[p.team || ""] = (counts[p.team || ""] || 0) + 1; });
    return counts;
  }, [selected]);

  const canAdd = (p: Player) => {
    if (selected.length >= MAX_PLAYERS) return false;
    if (selected.find((s) => s.player_id === p.player_id)) return false;
    if (creditsUsed + p.credits > BUDGET) return false;
    if ((teamCounts[p.team || ""] || 0) >= MAX_PER_TEAM) return false;
    return true;
  };

  const addPlayer = (p: Player) => {
    if (!canAdd(p)) return;
    setSelected([...selected, p]);
  };

  const removePlayer = (id: number) => {
    setSelected(selected.filter((p) => p.player_id !== id));
    if (captainId === id) setCaptainId(null);
    if (vcId === id) setVcId(null);
  };

  const allSquadPlayers = useMemo(() => {
    if (!matchData?.squads) return [];
    const all: (Player & { team: string })[] = [];
    Object.entries(matchData.squads).forEach(([team, players]) => {
      (players as any[]).forEach((p) => all.push({ ...p, team }));
    });
    return all;
  }, [matchData]);

  const filtered = allSquadPlayers.filter((p) => {
    if (search && !p.player_name.toLowerCase().includes(search.toLowerCase())) return false;
    if (roleFilter && p.role !== roleFilter) return false;
    return true;
  });

  const canSubmit = selected.length === MAX_PLAYERS && captainId && vcId && remaining >= 0;

  const handleSubmit = () => {
    if (!canSubmit || !teamName.trim()) return;
    createTeamMutation.mutate({
      match_id: matchId, // Send as string, not number
      team_name: teamName.trim(),
      player_ids: selected.map((p) => p.player_id),
      captain_id: captainId,
      vice_captain_id: vcId,
    });
  };

  if (isLoading) return (
    <ProtectedRoute><Layout><div className="container py-8"><Skeleton className="h-96" /></div></Layout></ProtectedRoute>
  );

  return (
    <ProtectedRoute>
      <Layout>
        <div className="container py-6 space-y-6">
          {/* Match Header */}
          <div className="gradient-stadium rounded-2xl p-6 text-stadium-foreground text-center">
            <div className="flex items-center justify-center gap-4 mb-2">
              <div className="flex items-center gap-2">
                {getTeamLogo(matchData?.team_home) && (
                  <img 
                    src={getTeamLogo(matchData?.team_home)} 
                    alt={matchData?.team_home}
                    className="h-8 w-8 object-contain"
                    onError={handleLogoError}
                  />
                )}
                <span className="text-2xl font-black">{matchData?.team_home}</span>
              </div>
              <span className="text-xl">vs</span>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black">{matchData?.team_away}</span>
                {getTeamLogo(matchData?.team_away) && (
                  <img 
                    src={getTeamLogo(matchData?.team_away)} 
                    alt={matchData?.team_away}
                    className="h-8 w-8 object-contain"
                    onError={handleLogoError}
                  />
                )}
              </div>
            </div>
            <p className="text-stadium-foreground/70 text-sm mt-1">{matchData?.venue}</p>
          </div>

          {/* Budget Bar */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2 text-sm">
                <span className="font-medium">Credits: {creditsUsed} / {BUDGET}</span>
                <span className="font-medium">Players: {selected.length} / {MAX_PLAYERS}</span>
              </div>
              <Progress value={(creditsUsed / BUDGET) * 100} className={remaining < 0 ? "[&>div]:bg-destructive" : ""} />
              {remaining < 0 && <p className="text-destructive text-xs mt-1">Budget exceeded by {Math.abs(remaining)} credits</p>}
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Player Selection */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex gap-2 flex-wrap">
                <div className="relative flex-1 min-w-[200px]">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search players..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
                </div>
                <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
                  className="px-3 py-2 rounded-md border border-input bg-card text-sm">
                  <option value="">All Roles</option>
                  <option>Batsman</option>
                  <option>Bowler</option>
                  <option>All-rounder</option>
                  <option>Wicket-Keeper</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {filtered.map((p) => {
                  const isSelected = !!selected.find((s) => s.player_id === p.player_id);
                  return (
                    <Card key={p.player_id} className={`transition-all ${isSelected ? "ring-2 ring-primary bg-primary/5" : "hover:shadow-md"}`}>
                      <CardContent className="p-3 flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm truncate">{p.player_name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${roleBadgeColor[p.role] || "bg-muted text-muted-foreground"}`}>{p.role}</span>
                            <div className="flex items-center gap-1">
                              {getTeamLogo(p.team) && (
                                <img 
                                  src={getTeamLogo(p.team)} 
                                  alt={p.team}
                                  className="h-3 w-3 object-contain"
                                  onError={handleLogoError}
                                />
                              )}
                              <span className="text-xs text-muted-foreground">{p.team}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="font-bold">{p.credits}c</Badge>
                          {isSelected ? (
                            <Button size="sm" variant="ghost" onClick={() => removePlayer(p.player_id)} className="h-8 w-8 p-0 text-destructive">
                              <X className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button size="sm" onClick={() => addPlayer(p)} disabled={!canAdd(p)} className="h-8">Add</Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* Selected Team Sidebar */}
            <div className="space-y-4">
              <Card>
                <CardContent className="p-4">
                  <h3 className="font-bold mb-3">Your XI ({selected.length}/{MAX_PLAYERS})</h3>
                  {selected.length === 0 && <p className="text-sm text-muted-foreground">Select players from the list</p>}
                  <div className="space-y-2">
                    {selected.map((p) => (
                      <div key={p.player_id} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          {captainId === p.player_id && <Crown className="h-4 w-4 text-secondary flex-shrink-0" />}
                          {vcId === p.player_id && <Star className="h-4 w-4 text-accent flex-shrink-0" />}
                          <span className="text-sm truncate">{p.player_name}</span>
                        </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          <Button size="sm" variant={captainId === p.player_id ? "default" : "ghost"}
                            onClick={() => { setCaptainId(p.player_id); if (vcId === p.player_id) setVcId(null); }}
                            className="h-6 w-6 p-0 text-xs" title="Captain">C</Button>
                          <Button size="sm" variant={vcId === p.player_id ? "default" : "ghost"}
                            onClick={() => { setVcId(p.player_id); if (captainId === p.player_id) setCaptainId(null); }}
                            className="h-6 w-6 p-0 text-xs" title="Vice Captain">V</Button>
                          <Button size="sm" variant="ghost" onClick={() => removePlayer(p.player_id)}
                            className="h-6 w-6 p-0 text-destructive"><X className="h-3 w-3" /></Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full mt-4" disabled={!canSubmit} onClick={() => setShowSubmit(true)}>
                    Create Team
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Submit Dialog */}
        <Dialog open={showSubmit} onOpenChange={setShowSubmit}>
          <DialogContent>
            <DialogHeader><DialogTitle>Name Your Team</DialogTitle></DialogHeader>
            <Input value={teamName} onChange={(e) => setTeamName(e.target.value)} placeholder="e.g. Thunder XI" />
            <DialogFooter>
              <Button onClick={handleSubmit} disabled={!teamName.trim() || createTeamMutation.isPending}>
                {createTeamMutation.isPending ? "Creating..." : "Submit Team"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </Layout>
    </ProtectedRoute>
  );
};

export default TeamSelection;
