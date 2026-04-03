import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MatchCard } from "@/components/MatchCard";
import { Trophy, BarChart3, Bot, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: todayMatch, isLoading: loadingToday } = useQuery({
    queryKey: ["matches", "today"],
    queryFn: () => api.get<any[]>("/matches/today").catch(() => []),
  });

  const { data: upcoming, isLoading: loadingUpcoming } = useQuery({
    queryKey: ["matches", "upcoming"],
    queryFn: () => api.get<any[]>("/matches/upcoming").catch(() => []),
  });

  const { data: aiUsage } = useQuery({
    queryKey: ["ai", "usage"],
    queryFn: () => api.get<{ questions_remaining: number; daily_limit: number }>("/ai/usage").catch(() => ({ questions_remaining: 10, daily_limit: 10 })),
    enabled: !!user,
  });

  return (
    <ProtectedRoute>
      <Layout>
        <div className="container py-8 space-y-8">
          {/* Welcome */}
          <div className="gradient-stadium rounded-2xl p-6 md:p-8 text-stadium-foreground">
            <h1 className="text-2xl md:text-3xl font-black">Welcome back, {user?.username}! 🏏</h1>
            <p className="text-stadium-foreground/70 mt-1">Ready for today's fantasy cricket action?</p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: Trophy, label: "Season Points", value: "—" },
              { icon: BarChart3, label: "Season Rank", value: "—" },
              { icon: Bot, label: "AI Questions Left", value: aiUsage ? `${aiUsage.questions_remaining}/${aiUsage.daily_limit}` : "—" },
            ].map((stat) => (
              <Card key={stat.label}>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <stat.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">{stat.label}</p>
                    <p className="text-lg font-bold">{stat.value}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Today's Match */}
          <section>
            <h2 className="text-xl font-bold mb-4">Today's Match</h2>
            {loadingToday ? (
              <Skeleton className="h-40 w-full max-w-md" />
            ) : todayMatch && todayMatch.length > 0 ? (
              <div className="max-w-md"><MatchCard match={todayMatch[0]} /></div>
            ) : (
              <Card><CardContent className="p-6 text-center text-muted-foreground">No matches scheduled today</CardContent></Card>
            )}
          </section>

          {/* Upcoming */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Upcoming Matches</h2>
              <Button variant="ghost" size="sm" onClick={() => navigate("/matches")} className="gap-1">
                View All <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
            {loadingUpcoming ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-40" />)}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {(upcoming || []).slice(0, 6).map((m: any) => <MatchCard key={m.match_id} match={m} />)}
              </div>
            )}
          </section>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default Dashboard;
