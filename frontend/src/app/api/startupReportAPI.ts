import BackendAPI from './BackendAPI'
import { components } from './generated-api-schema'

type GetStartupReportsResponse =
  components['schemas']['GetStartupReportsResponse']
type CreateStartupReportsRequest =
  components['schemas']['CreateStartupReportsRequest']
type DefaultSuccessResponse = components['schemas']['DefaultSuccessResponse']

const startupReportAPI = {
  getStartupReports: (): Promise<GetStartupReportsResponse> => {
    return BackendAPI.GET('/api/startup-report')
  },

  createStartupReports: (names: string[]): Promise<DefaultSuccessResponse> => {
    return BackendAPI.POST('/api/startup-report/create', {
      body: { names } as CreateStartupReportsRequest,
      params: {}
    })
  }
}

export default startupReportAPI
