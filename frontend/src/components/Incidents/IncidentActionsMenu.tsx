import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { IncidentPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteIncident from "../Incidents/DeleteIncident"
import EditIncident from "../Incidents/EditIncident"

interface IncidentActionsMenuProps {
  item: IncidentPublic
}

export const IncidentActionsMenu = ({ item }: IncidentActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditIncident item={item} onSuccess={() => setOpen(false)} />
        <DeleteIncident id={item.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
