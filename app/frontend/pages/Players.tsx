import { useState } from "react";
import { Layout } from "@/components/Layout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, Users, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getPlayerImageUrl, handleImageError } from "@/lib/player-utils";
import { getTeamLogo, handleLogoError } from "@/lib/team-utils";

const roleBadgeColor: Record<string, string> = {
  Batsman: "bg-accent/10 text-accent border-0",
  Bowler: "bg-primary/10 text-primary border-0",
  "All-rounder": "bg-secondary/10 text-secondary border-0",
  "Wicket-Keeper": "bg-destructive/10 text-destructive border-0",
};

const Players = () => {
  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const navigate = useNavigate();

  const params = new URLSearchParams();
  if (teamFilter) params.set("team", teamFilter);
  if (roleFilter) params.set("role", roleFilter);
  const qs = params.toString() ? `?${params.toString()}` : "";

  const { data: players, isLoading } = useQuery({
    queryKey: ["players", teamFilter, roleFilter],
    queryFn: () => api.get<any[]>(`/players${qs}`).catch(() => []),
  });

  const teams = [...new Set((players || []).map((p: any) => p.team).filter(Boolean))];

  const filtered = (players || []).filter((p: any) =>
    !search || p.player_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Layout>
      <div className="container py-8">
        <div className="flex items-center gap-3 mb-6">
          <Users className="h-7 w-7 text-primary" />
          <h1 className="text-2xl font-black">PSL 2026 Players</h1>
        </div>

        <div className="flex flex-wrap gap-3 mb-6">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search players..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
          </div>
          <select value={teamFilter} onChange={(e) => setTeamFilter(e.target.value)}
            className="px-3 py-2 rounded-md border border-input bg-card text-sm">
            <option value="">All Teams</option>
            {teams.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 rounded-md border border-input bg-card text-sm">
            <option value="">All Roles</option>
            <option>Batsman</option>
            <option>Bowler</option>
            <option>All-rounder</option>
            <option>Wicket-Keeper</option>
          </select>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-32" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((p: any) => (
              <Card key={p.player_id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate(`/players/${p.player_id}`)}>
                <CardContent className="p-4">
                  <div className="flex flex-col items-center mb-3">
                    <div className="relative w-20 h-20 rounded-full overflow-hidden mb-2 flex items-center justify-center bg-gradient-to-br from-primary/10 to-accent/10">
                      <img 
                        src={getPlayerImageUrl(p.player_name)}
                        alt={p.player_name}
                        className="w-full h-full object-cover"
                        onError={handleImageError}
                      />
                      <User className="absolute inset-0 m-auto h-10 w-10 text-primary/30 opacity-0 peer-[img:hidden]:opacity-100" />
                    </div>
                    <h3 className="font-bold text-sm text-center">{p.player_name}</h3>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${roleBadgeColor[p.role] || "bg-muted"}`}>{p.role}</span>
                    <Badge variant="secondary" className="font-bold">{p.credits}c</Badge>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground mb-3">
                    {getTeamLogo(p.team) && (
                      <img 
                        src={getTeamLogo(p.team)} 
                        alt={p.team}
                        className="h-4 w-4 object-contain"
                        onError={handleLogoError}
                      />
                    )}
                    <span>{p.team}</span>
                  </div>
                  <Button size="sm" variant="outline" className="w-full" onClick={(e) => { e.stopPropagation(); navigate(`/players/${p.player_id}`); }}>
                    View Profile
                  </Button>
                </CardContent>
              </Card>
            ))}
            {filtered.length === 0 && (
              <div className="col-span-full text-center py-12 text-muted-foreground">No players found</div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Players;
