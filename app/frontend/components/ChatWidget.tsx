import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Bot, Send, User, MessageCircle } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "ai";
  content: string;
}

const ChatWidget = () => {
  const [open, setOpen] = useState(false);
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
  }, [messages, open]);

  const handleSend = () => {
    if (!input.trim() || askMutation.isPending) return;
    const q = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    askMutation.mutate(q);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        className="fixed bottom-6 right-6 z-50 bg-primary text-white rounded-full p-4 shadow-lg hover:bg-primary/90 transition"
        onClick={() => setOpen((v) => !v)}
        aria-label="Open AI Assistant"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
      {/* Chat Widget Modal */}
      {open && (
        <div className="fixed bottom-20 right-6 z-50 w-[350px] max-h-[70vh] flex flex-col bg-background border rounded-xl shadow-2xl animate-fade-in">
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <span className="font-semibold">AI Assistant</span>
            </div>
            <button className="text-muted-foreground hover:text-primary" onClick={() => setOpen(false)}>&times;</button>
          </div>
          {/* Messages */}
          <Card className="flex-1 overflow-hidden rounded-none border-none shadow-none">
            <CardContent className="p-3 h-full overflow-y-auto space-y-3">
              {messages.length === 0 && (
                <div className="text-center py-8 text-muted-foreground space-y-2">
                  <Bot className="h-8 w-8 mx-auto text-primary/40" />
                  <p>Ask me anything about PSL 2026 players!</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-2 ${msg.role === "user" ? "justify-end" : ""}`}>
                  {msg.role === "ai" && (
                    <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-muted rounded-bl-md"
                  }`}>
                    {msg.content}
                  </div>
                  {msg.role === "user" && (
                    <div className="h-7 w-7 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-accent" />
                    </div>
                  )}
                </div>
              ))}
              {askMutation.isPending && (
                <div className="flex gap-2">
                  <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary animate-pulse" />
                  </div>
                  <div className="bg-muted rounded-2xl rounded-bl-md px-3 py-2 text-sm text-muted-foreground">
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </CardContent>
          </Card>
          {/* Input */}
          <div className="flex gap-2 p-3 border-t">
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
      )}
    </>
  );
};

export default ChatWidget;
