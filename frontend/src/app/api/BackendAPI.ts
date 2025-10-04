/* eslint-disable @typescript-eslint/no-explicit-any */
import createClient from 'openapi-fetch'
import type { paths } from './generated-api-schema'

const client = createClient<paths>({
  baseUrl: 'http://localhost:8081'
})

const BackendAPI = {
  GET: async <P extends keyof paths & string>(
    path: paths[P] extends { get: any } ? P : never,
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

  POST: async <P extends keyof paths & string>(
    path: paths[P] extends { post: any } ? P : never,
    options?: paths[P] extends { post: any }
      ? (paths[P]['post'] extends {
          requestBody: { content: { 'application/json': any } }
        }
          ? {
              body: paths[P]['post']['requestBody']['content']['application/json']
            }
          : object) &
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
