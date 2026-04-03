import { useParams, Link } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Trophy } from "lucide-react";

const Leaderboard = () => {
  const { matchId } = useParams();
  const isSeason = !matchId;
  const endpoint = isSeason ? "/fantasy/season/leaderboard" : `/fantasy/matchday/leaderboard/${matchId}`;

  const { data, isLoading } = useQuery({
    queryKey: ["leaderboard", matchId || "season"],
    queryFn: () => api.get<any[]>(endpoint).catch(() => []),
  });

  return (
    <Layout>
      <div className="container py-8 max-w-3xl">
        <div className="flex items-center gap-3 mb-6">
          <Trophy className="h-7 w-7 text-secondary" />
          <h1 className="text-2xl font-black">{isSeason ? "Season Leaderboard" : `Match Leaderboard`}</h1>
        </div>

        <div className="flex gap-2 mb-6">
          <Link to="/leaderboard/season">
            <Button variant={isSeason ? "default" : "outline"} size="sm">Season</Button>
          </Link>
        </div>

        <Card>
          <CardContent className="p-0">
            {isLoading ? <Skeleton className="h-64 m-4" /> : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Rank</TableHead>
                    <TableHead>Username</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead className="text-right">Points</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(data || []).map((entry: any) => (
                    <TableRow key={entry.rank}>
                      <TableCell className="font-bold">
                        {entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : `#${entry.rank}`}
                      </TableCell>
                      <TableCell>{entry.username}</TableCell>
                      <TableCell className="text-muted-foreground">{entry.team_name}</TableCell>
                      <TableCell className="text-right font-bold">{entry.total_points}</TableCell>
                    </TableRow>
                  ))}
                  {(!data || data.length === 0) && (
                    <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground py-8">No entries yet</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Leaderboard;
