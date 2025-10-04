/* eslint-disable @typescript-eslint/no-explicit-any */
import createClient from 'openapi-fetch'
import type { paths } from './generated-api-schema'

// Create a typed client using the auto-generated OpenAPI schema
const client = createClient<paths>({
  baseUrl: 'http://localhost:8081'
})

const BackendAPI = {
  /**
   * Type-safe GET request wrapper
   *
   * @template P - The API path type, must be a valid GET endpoint from the schema
   * @param path - The API endpoint path (e.g., '/api/startup-report')
   *               Only paths with GET methods are allowed at compile time
   * @param options - Optional parameters (query, header, path, cookie)
   *                 Type is inferred from the schema for the given path
   * @returns Promise resolving to the response data
   * @throws Error if the API returns an error response
   */
  GET: async <P extends keyof paths & string>(
    // First parameter: only allow paths that support GET
    path: paths[P] extends { get: any } ? P : never,
    // Second parameter: optional parameters based on the endpoint's requirements
    options?: paths[P] extends { get: any }
      ? paths[P]['get'] extends { parameters: any }
        ? paths[P]['get']['parameters']
        : never
      : never
  ) => {
    const response = await client.GET(path as any, options as any)

    if (response.error) {
      throw new Error(`API Error: ${JSON.stringify(response.error)}`)
    }

    return response.data
  },

  /**
   * Type-safe POST request wrapper
   *
   * @template P - The API path type, must be a valid POST endpoint from the schema
   * @param path - The API endpoint path (e.g., '/api/startup-report/create')
   *               Only paths with POST methods are allowed at compile time
   * @param options - Request options including:
   *                 - body: Request body typed from the schema
   *                 - params: Optional parameters (query, header, path, cookie)
   *                 Both are typed based on the schema for the given path
   * @returns Promise resolving to the response data
   * @throws Error if the API returns an error response
   */
  POST: async <P extends keyof paths & string>(
    // First parameter: only allow paths that support POST
    path: paths[P] extends { post: any } ? P : never,
    // Second parameter: intersection of body and params types
    options?: paths[P] extends { post: any }
      ? // If endpoint has a request body, require 'body' property with correct type
        (paths[P]['post'] extends {
          requestBody: { content: { 'application/json': any } }
        }
          ? {
              body: paths[P]['post']['requestBody']['content']['application/json']
            }
          : object) &
          // If endpoint has parameters, require 'params' property with correct type
          (paths[P]['post'] extends { parameters: any }
            ? { params: paths[P]['post']['parameters'] }
            : object)
      : never
  ) => {
    const response = await client.POST(path as any, options as any)

    if (response.error) {
      throw new Error(`API Error: ${JSON.stringify(response.error)}`)
    }

    return response.data
  }
}

export default BackendAPI
