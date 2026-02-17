import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft, Trash2 } from "lucide-react"

import { CommentsService, IncidentsService } from "@/client"
import type { CommentPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { useState } from "react"

export const Route = createFileRoute("/_layout/incidents/$id")({
  component: IncidentDetail,
  head: () => ({
    meta: [{ title: "Incident Detail - Incident Tracker" }],
  }),
})

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

function IncidentDetail() {
  const { id } = Route.useParams()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [commentContent, setCommentContent] = useState("")

  const { data: incident, isLoading } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => IncidentsService.readIncident({ id }),
  })

  const { data: commentsData } = useQuery({
    queryKey: ["comments", id],
    queryFn: () => CommentsService.readComments({ incidentId: id }),
    enabled: !!incident,
  })

  const addCommentMutation = useMutation({
    mutationFn: () =>
      CommentsService.createComment({
        incidentId: id,
        requestBody: { content: commentContent },
      }),
    onSuccess: () => {
      showSuccessToast("Comment added")
      setCommentContent("")
      queryClient.invalidateQueries({ queryKey: ["comments", id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId: string) =>
      CommentsService.deleteComment({ incidentId: id, commentId }),
    onSuccess: () => {
      showSuccessToast("Comment deleted")
      queryClient.invalidateQueries({ queryKey: ["comments", id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!incident) {
    return <div>Incident not found</div>
  }

  const status = incident.status ?? "open"
  const priority = incident.priority ?? "medium"
  const category = incident.category ?? "bug"
  const sConfig = statusConfig[status] ?? statusConfig.open
  const pConfig = priorityConfig[priority] ?? priorityConfig.medium

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Link to="/incidents">
          <Button variant="ghost" size="icon">
            <ArrowLeft />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{incident.title}</h1>
          <p className="text-sm text-muted-foreground font-mono">
            {incident.id}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <Badge variant={sConfig.variant} className="mt-1">
                {sConfig.label}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Priority</p>
              <Badge variant="outline" className={`mt-1 ${pConfig.className}`}>
                {pConfig.label}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Category</p>
              <p className="mt-1 text-sm">{categoryConfig[category] ?? category}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created</p>
              <p className="mt-1 text-sm">
                {incident.created_at
                  ? new Date(incident.created_at).toLocaleString()
                  : "N/A"}
              </p>
            </div>
            {incident.resolved_at && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                <p className="mt-1 text-sm">
                  {new Date(incident.resolved_at).toLocaleString()}
                </p>
              </div>
            )}
            <div className="sm:col-span-2">
              <p className="text-sm font-medium text-muted-foreground">Description</p>
              <p className="mt-1 text-sm">
                {incident.description || "No description provided"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comments ({commentsData?.count ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {commentsData?.data.map((comment: CommentPublic) => (
              <div
                key={comment.id}
                className="flex items-start justify-between rounded-md border p-3"
              >
                <div className="flex-1">
                  <p className="text-sm">{comment.content}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {comment.created_at
                      ? new Date(comment.created_at).toLocaleString()
                      : ""}
                  </p>
                </div>
                {(user?.is_superuser || user?.id === comment.author_id) && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-7 text-muted-foreground hover:text-destructive"
                    onClick={() => deleteCommentMutation.mutate(comment.id)}
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                )}
              </div>
            ))}

            {commentsData?.data.length === 0 && (
              <p className="text-sm text-muted-foreground">No comments yet</p>
            )}

            <div className="flex flex-col gap-2 pt-2 border-t">
              <Textarea
                placeholder="Add a comment..."
                value={commentContent}
                onChange={(e) => setCommentContent(e.target.value)}
                className="min-h-20"
              />
              <div className="flex justify-end">
                <Button
                  size="sm"
                  disabled={
                    !commentContent.trim() || addCommentMutation.isPending
                  }
                  onClick={() => addCommentMutation.mutate()}
                >
                  {addCommentMutation.isPending ? "Posting..." : "Add Comment"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
