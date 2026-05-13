"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileText, LogIn } from "lucide-react";
import { FormEvent, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/hooks/use-auth";
import { getErrorMessage } from "@/services/errors";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    try {
      await login({ email, password });
      router.replace("/dashboard");
    } catch (error) {
      toast.error(getErrorMessage(error, "Login failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <section className="panel w-full max-w-md p-6">
        <div className="mb-6 flex items-center gap-3">
          <div className="icon-btn" aria-hidden>
            <FileText size={20} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Enterprise AI PDF Chat</h1>
            <p className="muted text-sm">Sign in</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={onSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-semibold">Email</span>
            <input
              className="input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold">Password</span>
            <input
              className="input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button className="btn btn-primary w-full" type="submit" disabled={loading}>
            <LogIn size={18} />
            {loading ? "Signing in" : "Sign in"}
          </button>
        </form>

        <p className="muted mt-5 text-center text-sm">
          New here?{" "}
          <Link className="font-bold text-[var(--primary)]" href="/register">
            Create account
          </Link>
        </p>
      </section>
    </main>
  );
}
