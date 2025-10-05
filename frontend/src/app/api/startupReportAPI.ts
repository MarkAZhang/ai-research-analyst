import BackendAPI from './BackendAPI'
import { components } from './generated-api-schema'

type GetStartupReportsResponse =
  components['schemas']['GetStartupReportsResponse']
type DefaultSuccessResponse = components['schemas']['DefaultSuccessResponse']
type GetCurrentPromptResponse =
  components['schemas']['GetCurrentPromptResponse']
type StartupReportResponse = components['schemas']['StartupReportResponse']

const startupReportAPI = {
  /**
   * Fetch all available startup reports
   * @returns Promise with array of startup reports
   */
  getStartupReports: (): Promise<GetStartupReportsResponse> => {
    return BackendAPI.GET('/api/startup-report')
  },

  /**
   * Create startup reports for the provided company names
   * @param names - Array of company names to create reports for
   * @returns Promise with success response
   */
  createStartupReports: (names: string[]): Promise<DefaultSuccessResponse> => {
    return BackendAPI.POST('/api/startup-report/create', {
      body: { names },
      params: {}
    })
  },

  /**
   * Delete startup reports by their IDs
   * @param reportIds - Array of report IDs to delete
   * @returns Promise with success response
   */
  deleteStartupReports: (
    reportIds: number[]
  ): Promise<DefaultSuccessResponse> => {
    return BackendAPI.POST('/api/startup-report/delete', {
      body: { report_ids: reportIds },
      params: {}
    })
  },

  /**
   * Update the startup report prompt (creates a new prompt, preserving history)
   * @param prompt - The new prompt text
   * @returns Promise with success response
   */
  updatePrompt: (prompt: string): Promise<DefaultSuccessResponse> => {
    return BackendAPI.POST('/api/startup-report/update-prompt', {
      body: { prompt },
      params: {}
    })
  },

  /**
   * Get the current (most recent) startup report prompt
   * @returns Promise with the current prompt (empty string if none exists)
   */
  getCurrentPrompt: (): Promise<GetCurrentPromptResponse> => {
    return BackendAPI.GET('/api/startup-report/current-prompt')
  },

  /**
   * Get a single startup report by ID
   * @param reportId - The ID of the report to fetch
   * @returns Promise with the report details
   */
  getStartupReport: (reportId: number): Promise<StartupReportResponse> => {
    return BackendAPI.GET('/api/startup-report/{report_id}', {
      path: { report_id: reportId }
    })
  }
}

export default startupReportAPI
