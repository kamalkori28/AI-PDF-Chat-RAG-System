import type { LucideIcon } from "lucide-react";

export function StatCard({
  icon: Icon,
  label,
  value,
  loading
}: {
  icon: LucideIcon;
  label: string;
  value: number;
  loading?: boolean;
}) {
  return (
    <div className="panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <span className="muted text-sm font-bold">{label}</span>
        <Icon className="text-[var(--accent)]" size={20} />
      </div>
      {loading ? <div className="h-8 w-20 rounded skeleton" /> : <p className="text-3xl font-bold">{value}</p>}
    </div>
  );
}

