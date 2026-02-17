import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"
import { Link } from "@tanstack/react-router"

import type { IncidentPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { cn } from "@/lib/utils"
import { IncidentActionsMenu } from "./IncidentActionsMenu"

function CopyId({ id }: { id: string }) {
  const [copiedText, copy] = useCopyToClipboard()
  const isCopied = copiedText === id

  return (
    <div className="flex items-center gap-1.5 group">
      <span className="font-mono text-xs text-muted-foreground">{id}</span>
      <Button
        variant="ghost"
        size="icon"
        className="size-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copy(id)}
      >
        {isCopied ? (
          <Check className="size-3 text-green-500" />
        ) : (
          <Copy className="size-3" />
        )}
        <span className="sr-only">Copy ID</span>
      </Button>
    </div>
  )
}

const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  open: { label: "Open", variant: "outline" },
  in_progress: { label: "In Progress", variant: "default" },
  resolved: { label: "Resolved", variant: "secondary" },
}

const priorityConfig: Record<string, { label: string; className: string }> = {
  low: { label: "Low", className: "bg-slate-100 text-slate-700 border-slate-200" },
  medium: { label: "Medium", className: "bg-yellow-100 text-yellow-800 border-yellow-200" },
  high: { label: "High", className: "bg-orange-100 text-orange-800 border-orange-200" },
  critical: { label: "Critical", className: "bg-red-100 text-red-800 border-red-200" },
}

const categoryConfig: Record<string, string> = {
  bug: "Bug",
  feature_request: "Feature Request",
  question: "Question",
  documentation: "Documentation",
}

export const columns: ColumnDef<IncidentPublic>[] = [
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => <CopyId id={row.original.id} />,
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => (
      <Link
        to="/incidents/$id"
        params={{ id: row.original.id }}
        className="font-medium hover:underline"
      >
        {row.original.title}
      </Link>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status ?? "open"
      const config = statusConfig[status] ?? statusConfig.open
      return <Badge variant={config.variant}>{config.label}</Badge>
    },
  },
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => {
      const priority = row.original.priority ?? "medium"
      const config = priorityConfig[priority] ?? priorityConfig.medium
      return (
        <Badge variant="outline" className={config.className}>
          {config.label}
        </Badge>
      )
    },
  },
  {
    accessorKey: "category",
    header: "Category",
    cell: ({ row }) => {
      const category = row.original.category ?? "bug"
      return (
        <span className="text-sm text-muted-foreground">
          {categoryConfig[category] ?? category}
        </span>
      )
    },
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => {
      const description = row.original.description
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !description && "italic",
          )}
        >
          {description || "No description"}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <IncidentActionsMenu item={row.original} />
      </div>
    ),
  },
]
