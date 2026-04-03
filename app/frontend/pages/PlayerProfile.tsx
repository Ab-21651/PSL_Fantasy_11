import { useParams } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { User } from "lucide-react";
import { getPlayerImageUrl, handleImageError } from "@/lib/player-utils";
import { getTeamLogo, handleLogoError } from "@/lib/team-utils";

const PlayerProfile = () => {
  const { playerId } = useParams();

  const { data: player, isLoading } = useQuery({
    queryKey: ["player", playerId],
    queryFn: () => api.get<any>(`/players/${playerId}`),
  });

  const { data: stats } = useQuery({
    queryKey: ["player-stats", playerId],
    queryFn: () => api.get<any[]>(`/players/${playerId}/stats`).catch(() => []),
  });

  const { data: form } = useQuery({
    queryKey: ["player-form", playerId],
    queryFn: () => api.get<any[]>(`/players/${playerId}/form`).catch(() => []),
  });

  if (isLoading) return <Layout><div className="container py-8"><Skeleton className="h-96 max-w-2xl mx-auto" /></div></Layout>;

  return (
    <Layout>
      <div className="container py-8 max-w-2xl">
        <Card className="mb-6">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-24 w-24 rounded-full overflow-hidden bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center flex-shrink-0 relative">
              <img 
                src={getPlayerImageUrl(player?.player_name)}
                alt={player?.player_name}
                className="w-full h-full object-cover"
                onError={handleImageError}
              />
              <User className="absolute inset-0 m-auto h-12 w-12 text-primary/30 opacity-0 peer-[img:hidden]:opacity-100" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-black">{player?.player_name}</h1>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                <div className="flex items-center gap-1.5">
                  {getTeamLogo(player?.team) && (
                    <img 
                      src={getTeamLogo(player?.team)} 
                      alt={player?.team}
                      className="h-5 w-5 object-contain"
                      onError={handleLogoError}
                    />
                  )}
                  <span className="text-sm text-muted-foreground">{player?.team}</span>
                </div>
                <Badge variant="outline">{player?.role}</Badge>
                {player?.nationality && <span className="text-sm text-muted-foreground">{player?.nationality}</span>}
              </div>
            </div>
            <Badge className="text-lg font-bold">{player?.credits}c</Badge>
          </CardContent>
        </Card>

        <Tabs defaultValue="stats">
          <TabsList className="w-full">
            <TabsTrigger value="stats" className="flex-1">Career Stats</TabsTrigger>
            <TabsTrigger value="form" className="flex-1">Recent Form</TabsTrigger>
          </TabsList>

          <TabsContent value="stats">
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Season</TableHead>
                      <TableHead>M</TableHead>
                      <TableHead>Runs</TableHead>
                      <TableHead>Avg</TableHead>
                      <TableHead>SR</TableHead>
                      <TableHead>Wkts</TableHead>
                      <TableHead>Econ</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(stats || []).map((s: any, i: number) => (
                      <TableRow key={i}>
                        <TableCell className="font-medium">{s.season}</TableCell>
                        <TableCell>{s.matches}</TableCell>
                        <TableCell>{s.runs ?? "—"}</TableCell>
                        <TableCell>{s.average ?? "—"}</TableCell>
                        <TableCell>{s.strike_rate ?? "—"}</TableCell>
                        <TableCell>{s.wickets ?? "—"}</TableCell>
                        <TableCell>{s.economy ?? "—"}</TableCell>
                      </TableRow>
                    ))}
                    {(!stats || stats.length === 0) && (
                      <TableRow><TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No stats available</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="form">
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Opponent</TableHead>
                      <TableHead>Runs</TableHead>
                      <TableHead>Wkts</TableHead>
                      <TableHead>Pts</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(form || []).map((f: any, i: number) => (
                      <TableRow key={i}>
                        <TableCell>{f.match_date}</TableCell>
                        <TableCell>{f.opponent}</TableCell>
                        <TableCell>{f.runs_scored ?? "—"}</TableCell>
                        <TableCell>{f.wickets_taken ?? "—"}</TableCell>
                        <TableCell className="font-bold">{f.points_earned ?? "—"}</TableCell>
                      </TableRow>
                    ))}
                    {(!form || form.length === 0) && (
                      <TableRow><TableCell colSpan={5} className="text-center py-8 text-muted-foreground">No recent form data</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default PlayerProfile;
