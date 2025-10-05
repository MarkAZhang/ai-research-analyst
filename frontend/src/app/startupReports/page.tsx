'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronDown, Loader2, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import startupReportAPI from '@/app/api/startupReportAPI'
import { Button } from '@/components/lib/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger
} from '@/components/lib/dropdown-menu'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/lib/table'
import { StatusPill } from '@/components/StatusPill'
import { components } from '@/app/api/generated-api-schema'

dayjs.extend(relativeTime)

type StartupReport = components['schemas']['StartupReportResponse']

export default function StartupReportsPage(): React.JSX.Element {
  const router = useRouter()
  const [reports, setReports] = useState<StartupReport[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isCreating, setIsCreating] = useState<boolean>(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false)
  const [newReportsText, setNewReportsText] = useState<string>('')
  const [selectedReportIds, setSelectedReportIds] = useState<Set<number>>(
    new Set()
  )
  const [isDeleting, setIsDeleting] = useState<boolean>(false)
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false)
  const [isEditPromptOpen, setIsEditPromptOpen] = useState<boolean>(false)
  const [promptText, setPromptText] = useState<string>('')
  const [isUpdatingPrompt, setIsUpdatingPrompt] = useState<boolean>(false)

  const fetchReports = async (): Promise<void> => {
    try {
      setIsLoading(true)
      const response = await startupReportAPI.getStartupReports()
      setReports(response.reports)
    } catch (error) {
      toast.error('Failed to load startup reports')
      console.error('Error fetching reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCurrentPrompt = async (): Promise<void> => {
    try {
      const response = await startupReportAPI.getCurrentPrompt()
      setPromptText(response.prompt)
    } catch (error) {
      console.error('Error fetching current prompt:', error)
      // Don't show error toast for this, just silently fail
    }
  }

  useEffect(() => {
    fetchReports()
    fetchCurrentPrompt()
  }, [])

  const handleCreateReports = async (): Promise<void> => {
    const names: string[] = newReportsText
      .split('\n')
      .map((name) => name.trim())
      .filter((name) => name.length > 0)

    if (names.length === 0) {
      toast.error('Please enter at least one company name')
      return
    }

    try {
      setIsCreating(true)
      setIsDropdownOpen(false)
      await startupReportAPI.createStartupReports(names)
      toast.success(`Successfully requested ${names.length} report(s)`)
      setNewReportsText('')
      await fetchReports()
    } catch (error) {
      toast.error('Failed to create reports')
      console.error('Error creating reports:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleDeleteReports = async (): Promise<void> => {
    const count = selectedReportIds.size
    const confirmed = window.confirm(
      `Are you sure you want to delete ${count} report${count > 1 ? 's' : ''}?`
    )

    if (!confirmed) {
      return
    }

    try {
      setIsDeleting(true)
      await startupReportAPI.deleteStartupReports(Array.from(selectedReportIds))
      toast.success(
        `Successfully deleted ${count} report${count > 1 ? 's' : ''}`
      )
      setSelectedReportIds(new Set())
      await fetchReports()
    } catch (error) {
      toast.error('Failed to delete reports')
      console.error('Error deleting reports:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const toggleReportSelection = (reportId: number): void => {
    const newSelection = new Set(selectedReportIds)
    if (newSelection.has(reportId)) {
      newSelection.delete(reportId)
    } else {
      newSelection.add(reportId)
    }
    setSelectedReportIds(newSelection)
  }

  const handleRefreshTable = async (): Promise<void> => {
    try {
      setIsRefreshing(true)
      await fetchReports()
      toast.success('Table refreshed successfully')
    } catch (error) {
      toast.error('Failed to refresh table')
      console.error('Error refreshing table:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleUpdatePrompt = async (): Promise<void> => {
    if (!promptText.trim()) {
      toast.error('Please enter a prompt')
      return
    }

    try {
      setIsUpdatingPrompt(true)
      setIsEditPromptOpen(false)
      await startupReportAPI.updatePrompt(promptText)
      toast.success('Prompt updated successfully')
    } catch (error) {
      toast.error('Failed to update prompt')
      console.error('Error updating prompt:', error)
    } finally {
      setIsUpdatingPrompt(false)
    }
  }

  return (
    <div className="container mx-auto py-8 max-w-[1200px]">
      <h1 className="text-3xl font-bold mb-6">Startup Reports</h1>

      <div className="mb-4 flex justify-between items-center">
        <div className="flex gap-2">
          <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
            <DropdownMenuTrigger asChild>
              <Button disabled={isCreating} className="gap-2">
                {isCreating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
                Request New Reports
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-96 p-4" align="start">
              <textarea
                value={newReportsText}
                onChange={(e) => setNewReportsText(e.target.value)}
                placeholder="Enter company names (one per line)"
                className="w-full h-32 p-2 border rounded-md resize-none mb-2"
              />
              <Button onClick={handleCreateReports} className="w-full">
                Confirm
              </Button>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu
            open={isEditPromptOpen}
            onOpenChange={setIsEditPromptOpen}
          >
            <DropdownMenuTrigger asChild>
              <Button disabled={isUpdatingPrompt} className="gap-2">
                {isUpdatingPrompt ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
                Edit Report Instructions
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-[768px] p-4" align="start">
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder="Enter startup report instructions"
                className="w-full h-64 p-2 border rounded-md resize-none mb-2"
              />
              <Button onClick={handleUpdatePrompt} className="w-full">
                Confirm
              </Button>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            onClick={handleRefreshTable}
            disabled={isRefreshing}
            variant="outline"
            className="gap-2"
          >
            <RefreshCw
              className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`}
            />
            Refresh Table
          </Button>
        </div>

        {selectedReportIds.size > 0 && (
          <Button
            onClick={handleDeleteReports}
            disabled={isDeleting}
            variant="destructive"
            className="gap-2"
          >
            {isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Delete Reports
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12"></TableHead>
              <TableHead>Startup Name</TableHead>
              <TableHead>Requested At</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-gray-500">
                  No reports found
                </TableCell>
              </TableRow>
            ) : (
              reports.map((report) => {
                const statusStateMap: Record<
                  string,
                  'initializing' | 'processing' | 'succeeded' | 'failed'
                > = {
                  pending: 'initializing',
                  started: 'processing',
                  completed: 'succeeded',
                  failed: 'failed'
                }
                const statusLabelMap: Record<string, string> = {
                  pending: 'Pending',
                  started: 'Processing',
                  completed: 'Completed',
                  failed: 'Failed'
                }

                return (
                  <TableRow
                    key={report.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => router.push(`/startupReports/${report.id}`)}
                  >
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedReportIds.has(report.id)}
                        onChange={() => toggleReportSelection(report.id)}
                        disabled={isDeleting}
                        className="cursor-pointer"
                      />
                    </TableCell>
                    <TableCell className="font-bold">{report.name}</TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {dayjs(report.created_at).fromNow()}
                    </TableCell>
                    <TableCell>
                      <StatusPill
                        state={statusStateMap[report.generation_status]}
                        label={statusLabelMap[report.generation_status]}
                      />
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
