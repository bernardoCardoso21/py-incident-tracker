import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { IncidentsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddIncident from "@/components/Incidents/AddIncident"
import { columns } from "@/components/Incidents/columns"
import PendingIncidents from "@/components/Pending/PendingIncidents"

function getIncidentsQueryOptions() {
  return {
    queryFn: () => IncidentsService.readIncidents({ skip: 0, limit: 100 }),
    queryKey: ["incidents"],
  }
}

export const Route = createFileRoute("/_layout/incidents")({
  component: Incidents,
  head: () => ({
    meta: [
      {
        title: "Incidents - Incident Tracker",
      },
    ],
  }),
})

function IncidentsTableContent() {
  const { data: incidents } = useSuspenseQuery(getIncidentsQueryOptions())

  if (incidents.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any incidents yet</h3>
        <p className="text-muted-foreground">Add a new incident to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={incidents.data} />
}

function IncidentsTable() {
  return (
    <Suspense fallback={<PendingIncidents />}>
      <IncidentsTableContent />
    </Suspense>
  )
}

function Incidents() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Incidents</h1>
          <p className="text-muted-foreground">Create and manage your incidents</p>
        </div>
        <AddIncident />
      </div>
      <IncidentsTable />
    </div>
  )
}
