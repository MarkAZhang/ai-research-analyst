// Example usage demonstrating type-safe API calls with inferred response types

import startupReportAPI from './startupReportAPI'

async function exampleUsage() {
  // GET request - response type is automatically inferred from the schema
  const reportsResponse = await startupReportAPI.getStartupReports()

  // TypeScript knows the exact shape of the response:
  // reportsResponse.reports is an array of StartupReportResponse objects
  reportsResponse.reports.forEach((report) => {
    console.log(report.id) // number
    console.log(report.name) // string
    console.log(report.created_at) // string
    console.log(report.read_by_user) // boolean
    console.log(report.generation_status) // string
    console.log(report.report_text) // string

    // TypeScript will error if you try to access a property that doesn't exist:
    // console.log(report.nonexistent) // Error: Property 'nonexistent' does not exist
  })

  // POST request - response type is automatically inferred from the schema
  const createResponse = await startupReportAPI.createStartupReports([
    'Company A',
    'Company B'
  ])

  // TypeScript knows this returns DefaultSuccessResponse:
  console.log(createResponse.success) // boolean

  // TypeScript will error if you try to access a property that doesn't exist:
  // console.log(createResponse.nonexistent) // Error: Property 'nonexistent' does not exist
}

export default exampleUsage
