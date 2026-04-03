import { lazy, Suspense } from "react";
import { Navbar } from "./Navbar";

// Lazy load ChatWidget
const ChatWidget = lazy(() => import("./ChatWidget"));

export const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen flex flex-col">
    <Navbar />
    <main className="flex-1">{children}</main>
    <Suspense fallback={null}>
      <ChatWidget />
    </Suspense>
  </div>
);
