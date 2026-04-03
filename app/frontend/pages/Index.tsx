import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Layout } from "@/components/Layout";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { MatchCard } from "@/components/MatchCard";
import { Trophy, Bot, Users, BarChart3, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

const features = [
  { icon: Users, title: "Pick 11 Players", desc: "Build your dream XI with a 100-credit budget" },
  { icon: Bot, title: "AI Insights", desc: "Get AI-powered player analysis and recommendations" },
  { icon: Trophy, title: "Leaderboards", desc: "Compete on daily and season leaderboards" },
  { icon: BarChart3, title: "Live Points", desc: "Track your team's performance in real-time" },
];

const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { data: todayMatch } = useQuery({
    queryKey: ["matches", "today"],
    queryFn: () => api.get<any[]>("/matches/today").catch(() => []),
  });

  return (
    <Layout>
      {/* Hero */}
      <section className="gradient-hero text-stadium-foreground">
        <div className="container py-20 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-2xl mx-auto text-center"
          >
            <span className="text-6xl md:text-7xl block mb-4">🏏</span>
            <h1 className="text-4xl md:text-6xl font-black tracking-tight mb-4">
              Create Your Dream <span className="text-gradient-gold">PSL Team</span>
            </h1>
            <p className="text-lg md:text-xl text-stadium-foreground/70 mb-8">
              Pakistan Super League 2026 Fantasy Cricket. Pick players, earn points, dominate leaderboards.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              {isAuthenticated ? (
                <Button size="lg" onClick={() => navigate("/dashboard")} className="gap-2 text-base font-bold">
                  Go to Dashboard <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <>
                  <Button size="lg" onClick={() => navigate("/register")} className="gap-2 text-base font-bold">
                    Join Now <ArrowRight className="h-4 w-4" />
                  </Button>
                  <Button size="lg" variant="outline" onClick={() => navigate("/login")}
                    className="text-base border-stadium-foreground/30 text-stadium-foreground hover:bg-stadium-foreground/10">
                    Login
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Today's Match */}
      {todayMatch && todayMatch.length > 0 && (
        <section className="container py-12">
          <h2 className="text-2xl font-bold mb-4 text-center">Today's Match</h2>
          <div className="max-w-md mx-auto">
            <MatchCard match={todayMatch[0]} />
          </div>
        </section>
      )}

      {/* Features */}
      <section className="container py-16">
        <h2 className="text-2xl font-bold mb-8 text-center">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i, duration: 0.4 }}
            >
              <Card className="h-full hover:shadow-md transition-shadow border-border/50">
                <CardContent className="p-6 text-center">
                  <div className="inline-flex items-center justify-center h-12 w-12 rounded-xl bg-primary/10 text-primary mb-4">
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-bold mb-1">{f.title}</h3>
                  <p className="text-sm text-muted-foreground">{f.desc}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-muted/30">
        <div className="container py-8 text-center text-sm text-muted-foreground">
          <p>🏏 CricMind — PSL 2026 Fantasy Cricket</p>
        </div>
      </footer>
    </Layout>
  );
};

export default Landing;
