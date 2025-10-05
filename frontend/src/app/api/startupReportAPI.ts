import BackendAPI from './BackendAPI'
import { components } from './generated-api-schema'

type GetStartupReportsResponse =
  components['schemas']['GetStartupReportsResponse']
type DefaultSuccessResponse = components['schemas']['DefaultSuccessResponse']

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
  }
}

export default startupReportAPI
