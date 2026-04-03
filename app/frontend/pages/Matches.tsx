import { Layout } from "@/components/Layout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { MatchCard } from "@/components/MatchCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar } from "lucide-react";

const Matches = () => {
  const { data: matches, isLoading } = useQuery({
    queryKey: ["matches", "all"],
    queryFn: () => api.get<any[]>("/matches/all").catch(() => []),
  });

  // Group by date
  const grouped = (matches || []).reduce((acc: Record<string, any[]>, m: any) => {
    const date = m.match_date || "TBD";
    if (!acc[date]) acc[date] = [];
    acc[date].push(m);
    return acc;
  }, {});

  return (
    <Layout>
      <div className="container py-8">
        <div className="flex items-center gap-3 mb-6">
          <Calendar className="h-7 w-7 text-primary" />
          <h1 className="text-2xl font-black">PSL 2026 Schedule</h1>
        </div>

        {isLoading ? (
          <div className="space-y-4">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-40" />)}</div>
        ) : (
          <div className="space-y-8">
            {Object.entries(grouped).map(([date, dateMatches]) => (
              <div key={date}>
                <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">{date}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {(dateMatches as any[]).map((m: any) => <MatchCard key={m.match_id} match={m} />)}
                </div>
              </div>
            ))}
            {Object.keys(grouped).length === 0 && (
              <div className="text-center py-12 text-muted-foreground">No matches found</div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Matches;
