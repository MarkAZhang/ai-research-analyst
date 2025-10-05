import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import StartupReportsPage from '../page'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn()
}))

// Mock the API module
jest.mock('@/app/api/startupReportAPI', () => ({
  __esModule: true,
  default: {
    getStartupReports: jest.fn(),
    getCurrentPrompt: jest.fn(),
    createStartupReports: jest.fn(),
    deleteStartupReports: jest.fn(),
    updatePrompt: jest.fn(),
    getStartupReport: jest.fn()
  }
}))

import startupReportAPI from '@/app/api/startupReportAPI'
const mockStartupReportAPI = startupReportAPI as jest.Mocked<
  typeof startupReportAPI
>

// Mock dayjs to make tests deterministic
jest.mock('dayjs', () => {
  const originalDayjs = jest.requireActual('dayjs')
  const mockDayjs = (date?: string | Date) => {
    const instance = originalDayjs(date)
    instance.fromNow = () => '2 hours ago'
    return instance
  }
  mockDayjs.extend = originalDayjs.extend
  return mockDayjs
})

const mockPush = jest.fn()
;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })

// Sample test data
const sampleReports = [
  {
    id: 1,
    name: 'Acme Corp',
    created_at: '2024-01-01T10:00:00Z',
    read_by_user: false,
    generation_status: 'completed',
    report_text: 'Report text',
    prompt_text: 'Test prompt'
  },
  {
    id: 2,
    name: 'Beta Inc',
    created_at: '2024-01-02T10:00:00Z',
    read_by_user: false,
    generation_status: 'pending',
    report_text: '',
    prompt_text: 'Test prompt'
  }
]

// Mock window.confirm
const mockConfirm = jest.fn()
global.confirm = mockConfirm

describe('StartupReportsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Default API mocks
    mockStartupReportAPI.getStartupReports.mockResolvedValue({
      reports: sampleReports
    })
    mockStartupReportAPI.getCurrentPrompt.mockResolvedValue({
      prompt: 'Default prompt text'
    })
    mockStartupReportAPI.createStartupReports.mockResolvedValue({
      success: true
    })
    mockStartupReportAPI.deleteStartupReports.mockResolvedValue({
      success: true
    })
    mockStartupReportAPI.updatePrompt.mockResolvedValue({ success: true })
  })

  describe('Initial Loading', () => {
    it('should show loading spinner initially and then display reports', async () => {
      render(<StartupReportsPage />)

      // Loading spinner should be visible
      expect(
        screen.getByRole('heading', { name: /startup reports/i })
      ).toBeInTheDocument()
      const loader = document.querySelector('.animate-spin')
      expect(loader).toBeInTheDocument()

      // Wait for reports to load
      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
        expect(screen.getByText('Beta Inc')).toBeInTheDocument()
      })
    })

    it('should show empty state when no reports exist', async () => {
      mockStartupReportAPI.getStartupReports.mockResolvedValue({ reports: [] })
      mockStartupReportAPI.getCurrentPrompt.mockResolvedValue({ prompt: '' })

      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('No reports found')).toBeInTheDocument()
      })
    })
  })

  describe('Server Error Handling', () => {
    it('should handle server error when fetching reports', async () => {
      mockStartupReportAPI.getStartupReports.mockRejectedValue(
        new Error('Server error')
      )
      mockStartupReportAPI.getCurrentPrompt.mockResolvedValue({ prompt: '' })

      render(<StartupReportsPage />)

      await waitFor(() => {
        // Should show empty state after error
        expect(screen.getByText('No reports found')).toBeInTheDocument()
      })
    })
  })

  describe('Creating Reports', () => {
    it('should allow creating new reports', async () => {
      const user = userEvent.setup()
      // Start with no reports
      mockStartupReportAPI.getStartupReports.mockResolvedValueOnce({
        reports: []
      })

      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('No reports found')).toBeInTheDocument()
      })

      // Set up for after creation
      mockStartupReportAPI.getStartupReports.mockResolvedValueOnce({
        reports: sampleReports
      })

      // Open the create dropdown
      const createButton = screen.getByRole('button', {
        name: /request new reports/i
      })
      await user.click(createButton)

      // Wait for dropdown to open and enter company names
      const textarea =
        await screen.findByPlaceholderText(/enter company names/i)
      await user.clear(textarea)
      await user.type(textarea, 'New Company{Enter}Another Company')

      // Click confirm
      const confirmButton = screen.getByRole('button', { name: /confirm/i })
      await user.click(confirmButton)

      await waitFor(() => {
        expect(mockStartupReportAPI.createStartupReports).toHaveBeenCalledWith([
          'New Company',
          'Another Company'
        ])
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })
    })

    it('should show error when creating reports with empty input', async () => {
      const user = userEvent.setup()
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Open the create dropdown
      const createButton = screen.getByRole('button', {
        name: /request new reports/i
      })
      await user.click(createButton)

      // Wait for dropdown to open then click confirm without entering any names
      const confirmButton = await screen.findByRole('button', {
        name: /confirm/i
      })
      await user.click(confirmButton)

      // Should not make API call
      await waitFor(() => {
        expect(mockStartupReportAPI.createStartupReports).not.toHaveBeenCalled()
      })
    })
  })

  describe('Deleting Reports', () => {
    it('should allow deleting selected reports', async () => {
      mockConfirm.mockReturnValue(true)

      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Set up response after delete
      mockStartupReportAPI.getStartupReports.mockResolvedValueOnce({
        reports: [sampleReports[1]]
      })

      // Select a report
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0])

      // Delete button should appear
      const deleteButton = await screen.findByRole('button', {
        name: /delete reports/i
      })
      expect(deleteButton).toBeInTheDocument()

      // Click delete
      fireEvent.click(deleteButton)

      // Confirm dialog should be called
      expect(mockConfirm).toHaveBeenCalledWith(
        'Are you sure you want to delete 1 report?'
      )

      await waitFor(() => {
        expect(mockStartupReportAPI.deleteStartupReports).toHaveBeenCalledWith([
          1
        ])
        expect(screen.queryByText('Acme Corp')).not.toBeInTheDocument()
        expect(screen.getByText('Beta Inc')).toBeInTheDocument()
      })
    })

    it('should not delete when user cancels confirmation', async () => {
      mockConfirm.mockReturnValue(false)

      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Select a report
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0])

      // Delete button should appear
      const deleteButton = await screen.findByRole('button', {
        name: /delete reports/i
      })

      // Click delete
      fireEvent.click(deleteButton)

      // Confirm should be called but delete shouldn't happen
      expect(mockConfirm).toHaveBeenCalled()
      expect(mockStartupReportAPI.deleteStartupReports).not.toHaveBeenCalled()

      // Reports should still be there
      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })
    })
  })

  describe('Refreshing Table', () => {
    it('should refresh the table when refresh button is clicked', async () => {
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Click refresh button
      const refreshButton = screen.getByRole('button', {
        name: /refresh table/i
      })
      const initialCallCount =
        mockStartupReportAPI.getStartupReports.mock.calls.length

      fireEvent.click(refreshButton)

      // Should make additional API calls
      await waitFor(() => {
        expect(
          mockStartupReportAPI.getStartupReports.mock.calls.length
        ).toBeGreaterThan(initialCallCount)
      })
    })
  })

  describe('Updating Prompt', () => {
    it('should allow updating the report instructions', async () => {
      const user = userEvent.setup()
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Open edit prompt dropdown
      const editButton = screen.getByRole('button', {
        name: /edit report instructions/i
      })
      await user.click(editButton)

      // Prompt textarea should be populated with current prompt
      const promptTextarea = await screen.findByPlaceholderText(
        /enter startup report instructions/i
      )
      expect(promptTextarea).toHaveValue('Default prompt text')

      // Update the prompt
      await user.clear(promptTextarea)
      await user.type(promptTextarea, 'New prompt text')

      // Click confirm
      const confirmButtons = screen.getAllByRole('button', { name: /confirm/i })
      await user.click(confirmButtons[confirmButtons.length - 1])

      await waitFor(() => {
        expect(mockStartupReportAPI.updatePrompt).toHaveBeenCalledWith(
          'New prompt text'
        )
      })
    })

    it('should show error when updating prompt with empty input', async () => {
      const user = userEvent.setup()
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Open edit prompt dropdown
      const editButton = screen.getByRole('button', {
        name: /edit report instructions/i
      })
      await user.click(editButton)

      // Clear the prompt
      const promptTextarea = await screen.findByPlaceholderText(
        /enter startup report instructions/i
      )
      await user.clear(promptTextarea)

      // Click confirm
      const confirmButtons = screen.getAllByRole('button', { name: /confirm/i })
      await user.click(confirmButtons[confirmButtons.length - 1])

      // Should not make API call
      await waitFor(() => {
        expect(mockStartupReportAPI.updatePrompt).not.toHaveBeenCalled()
      })
    })
  })

  describe('Navigation', () => {
    it('should navigate to report detail page when clicking a report row', async () => {
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Click on the report row (clicking on the name specifically)
      const reportRow = screen.getByText('Acme Corp')
      fireEvent.click(reportRow)

      // Should navigate to detail page
      expect(mockPush).toHaveBeenCalledWith('/startupReports/1')
    })

    it('should not navigate when clicking on checkbox', async () => {
      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
      })

      // Click on checkbox
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0])

      // Should not navigate
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('Report Status Display', () => {
    it('should display correct status pills for different statuses', async () => {
      const reportsWithDifferentStatuses = [
        { ...sampleReports[0], generation_status: 'pending' },
        {
          ...sampleReports[1],
          generation_status: 'started',
          id: 3,
          name: 'Gamma LLC'
        },
        {
          ...sampleReports[0],
          generation_status: 'completed',
          id: 4,
          name: 'Delta Corp'
        },
        {
          ...sampleReports[0],
          generation_status: 'failed',
          id: 5,
          name: 'Epsilon Inc'
        }
      ]

      mockStartupReportAPI.getStartupReports.mockResolvedValue({
        reports: reportsWithDifferentStatuses
      })

      render(<StartupReportsPage />)

      await waitFor(() => {
        expect(screen.getByText('Acme Corp')).toBeInTheDocument()
        expect(screen.getByText('Gamma LLC')).toBeInTheDocument()
        expect(screen.getByText('Delta Corp')).toBeInTheDocument()
        expect(screen.getByText('Epsilon Inc')).toBeInTheDocument()
      })

      // Check for status labels
      expect(screen.getByText('Pending')).toBeInTheDocument()
      expect(screen.getByText('Processing')).toBeInTheDocument()
      expect(screen.getByText('Completed')).toBeInTheDocument()
      expect(screen.getByText('Failed')).toBeInTheDocument()
    })
  })
})
