import BackendAPI from './BackendAPI'

const startupReportAPI = {
  /**
   * Fetch all available startup reports
   * @returns Promise with array of startup reports
   */
  getStartupReports: () => {
    return BackendAPI.GET('/api/startup-report')
  },

  /**
   * Create startup reports for the provided company names
   * @param names - Array of company names to create reports for
   * @returns Promise with success response
   */
  createStartupReports: (names: string[]) => {
    return BackendAPI.POST('/api/startup-report/create', {
      body: { names },
      params: {}
    })
  }
}

export default startupReportAPI
