'use client'

import { useState, useEffect, useRef } from 'react'
import { ChevronDown, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import startupReportAPI from '@/app/api/startupReportAPI'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { components } from '@/app/api/generated-api-schema'

type StartupReport = components['schemas']['StartupReportResponse']

export default function StartupReportsPage(): React.JSX.Element {
  const [reports, setReports] = useState<StartupReport[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isCreating, setIsCreating] = useState<boolean>(false)
  const [showDropdown, setShowDropdown] = useState<boolean>(false)
  const [newReportsText, setNewReportsText] = useState<string>('')
  const dropdownRef = useRef<HTMLDivElement>(null)

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

  useEffect(() => {
    fetchReports()
  }, [])

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false)
      }
    }

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showDropdown])

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
      setShowDropdown(false)
      await startupReportAPI.createStartupReports(names)
      toast.success(`Successfully created ${names.length} report(s)`)
      setNewReportsText('')
      await fetchReports()
    } catch (error) {
      toast.error('Failed to create reports')
      console.error('Error creating reports:', error)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="container mx-auto py-8 max-w-[1200px]">
      <h1 className="text-3xl font-bold mb-6">Startup Reports</h1>

      <div className="mb-4 relative" ref={dropdownRef}>
        <Button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={isCreating}
          className="gap-2"
        >
          {isCreating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
          Add New Reports
        </Button>

        {showDropdown && (
          <div className="absolute top-full mt-2 w-96 bg-white border rounded-md shadow-lg p-4 z-10">
            <textarea
              value={newReportsText}
              onChange={(e) => setNewReportsText(e.target.value)}
              placeholder="Enter company names (one per line)"
              className="w-full h-32 p-2 border rounded-md resize-none mb-2"
            />
            <Button onClick={handleCreateReports} className="w-full">
              Confirm
            </Button>
          </div>
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
              <TableHead>Name</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Generation Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-gray-500">
                  No reports found
                </TableCell>
              </TableRow>
            ) : (
              reports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell>{report.name}</TableCell>
                  <TableCell>
                    {new Date(report.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{report.generation_status}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
