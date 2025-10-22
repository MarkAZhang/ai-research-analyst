'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import startupReportAPI from '@/app/api/startupReportAPI'
import { Button } from '@/components/lib/button'
import { components } from '@/app/api/generated-api-schema'

type StartupReport = components['schemas']['StartupReportResponse']

export default function StartupReportDetailsPage(): React.JSX.Element {
  const params = useParams()
  const router = useRouter()
  const reportId = Number(params.id)

  const [report, setReport] = useState<StartupReport | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [showPromptModal, setShowPromptModal] = useState<boolean>(false)

  useEffect(() => {
    const fetchReport = async (): Promise<void> => {
      try {
        setIsLoading(true)
        const response = await startupReportAPI.getStartupReport(reportId)
        setReport(response)
      } catch (error) {
        // Error toast is shown by BackendAPI
        console.error('Error fetching report:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (reportId) {
      fetchReport()
    }
  }, [reportId])

  const handleBackClick = (): void => {
    router.push('/startupReports')
  }

  const getStatusDisplay = (): { text: string; color: string } | null => {
    if (!report) return null

    switch (report.generation_status) {
      case 'pending':
        return {
          text: 'Report generation is pending...',
          color: 'text-gray-600'
        }
      case 'started':
        return {
          text: 'Report is being generated...',
          color: 'text-gray-600'
        }
      case 'failed':
        return { text: 'Report generation failed', color: 'text-red-600' }
      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 max-w-[1200px]">
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="container mx-auto py-8 max-w-[1200px]">
        <p className="text-center text-gray-500">Report not found</p>
      </div>
    )
  }

  const statusDisplay = getStatusDisplay()

  return (
    <div className="container mx-auto py-8 max-w-[1200px] px-[50px]">
      <button
        onClick={handleBackClick}
        className="flex items-center gap-1 text-sm text-gray-700 hover:text-gray-900 mb-4 cursor-pointer"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Reports
      </button>

      <h1 className="text-3xl font-bold mb-2">{report.name}</h1>

      <div className="mb-6">
        <button
          onClick={() => setShowPromptModal(true)}
          className="flex items-center text-xs text-gray-500 hover:text-gray-900 cursor-pointer"
        >
          View Prompt
        </button>
      </div>

      {report.generation_status === 'completed' ? (
        <div className="prose max-w-none">
          <ReactMarkdown>{report.report_text}</ReactMarkdown>
        </div>
      ) : (
        statusDisplay && (
          <div className={`text-sm ${statusDisplay.color} italic`}>
            {statusDisplay.text}
          </div>
        )
      )}

      {showPromptModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowPromptModal(false)}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-xl font-bold mb-4">Report Prompt</h2>
            <div className="whitespace-pre-wrap mb-4">
              {report.prompt_text || 'No prompt available'}
            </div>
            <Button onClick={() => setShowPromptModal(false)}>Close</Button>
          </div>
        </div>
      )}
    </div>
  )
}
