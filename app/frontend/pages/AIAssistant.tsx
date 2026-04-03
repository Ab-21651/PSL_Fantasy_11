import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Bot, Send, User } from "lucide-react";

interface Message {
  role: "user" | "ai";
  content: string;
}

const AIAssistant = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: usage, refetch: refetchUsage } = useQuery({
    queryKey: ["ai", "usage"],
    queryFn: () => api.get<{ questions_asked: number; questions_remaining: number; daily_limit: number }>("/ai/usage"),
  });

  const askMutation = useMutation({
    mutationFn: (question: string) => api.post<{ answer: string; remaining_questions: number }>("/ai/ask", { question }),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "ai", content: data.answer }]);
      refetchUsage();
    },
    onError: (err: any) => {
      setMessages((prev) => [...prev, { role: "ai", content: `Error: ${err.message}` }]);
    },
  });

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || askMutation.isPending) return;
    const q = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    askMutation.mutate(q);
  };

  return (
    <ProtectedRoute>
      <Layout>
        <div className="container py-6 flex flex-col h-[calc(100vh-4rem)] max-w-2xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">AI Assistant</h1>
            </div>
            {usage && (
              <span className="text-sm text-muted-foreground">
                {usage.questions_remaining}/{usage.daily_limit} questions left
              </span>
            )}
          </div>

          {/* Messages */}
          <Card className="flex-1 overflow-hidden">
            <CardContent className="p-4 h-full overflow-y-auto space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12 text-muted-foreground space-y-4">
                  <Bot className="h-12 w-12 mx-auto text-primary/40" />
                  <p>Ask me anything about PSL 2026 players!</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {["Is Babar Azam in good form?", "Best bowlers for today?", "Compare Shaheen vs Naseem Shah"].map((q) => (
                      <Button key={q} variant="outline" size="sm" onClick={() => { setInput(q); }}>
                        {q}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
                  {msg.role === "ai" && (
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-muted rounded-bl-md"
                  }`}>
                    {msg.content}
                  </div>
                  {msg.role === "user" && (
                    <div className="h-8 w-8 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-accent" />
                    </div>
                  )}
                </div>
              ))}
              {askMutation.isPending && (
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary animate-pulse" />
                  </div>
                  <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-2.5 text-sm text-muted-foreground">
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </CardContent>
          </Card>

          {/* Input */}
          <div className="flex gap-2 mt-4">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about players, stats, matchups..."
              disabled={askMutation.isPending || (usage?.questions_remaining === 0)}
            />
            <Button onClick={handleSend} disabled={!input.trim() || askMutation.isPending} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default AIAssistant;
