"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FilePlus2, UserPlus } from "lucide-react";
import { FormEvent, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/hooks/use-auth";
import { getErrorMessage } from "@/services/errors";

export default function RegisterPage() {
  const router = useRouter();
  const { register, login } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    try {
      await register({ full_name: fullName, email, password });
      await login({ email, password });
      router.replace("/dashboard");
    } catch (error) {
      toast.error(getErrorMessage(error, "Registration failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <section className="panel w-full max-w-md p-6">
        <div className="mb-6 flex items-center gap-3">
          <div className="icon-btn" aria-hidden>
            <FilePlus2 size={20} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Create Account</h1>
            <p className="muted text-sm">Enterprise AI PDF Chat</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={onSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-semibold">Full name</span>
            <input
              className="input"
              value={fullName}
              autoComplete="name"
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          </label>

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
              autoComplete="new-password"
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button className="btn btn-primary w-full" type="submit" disabled={loading}>
            <UserPlus size={18} />
            {loading ? "Creating" : "Create account"}
          </button>
        </form>

        <p className="muted mt-5 text-center text-sm">
          Already registered?{" "}
          <Link className="font-bold text-[var(--primary)]" href="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
