# Frontend style

### High-level Layout
- app - the top level for application-code
  - api - API-related code
  - components - generic components go here, including shadcn/ui components.
  - pages - each page belongs in its own folder, i.e, startupReports.

### Modularity
Bias towards separate files for distinct React components, instead of putting multiple React components into a single file. An exception would be if there are multiple very small (i.e. 10-ish lines) React components which are all related.

Bias towards grouping related components and files into sub-directories with a descriptive name, instead of having many files in a top-level directory.

### Type signatures
Explicitly type all variables and function return values, except for functions that return void.

### Testing
We use Jest with React Testing Library (RTL) and Mock Servier Worker (MSW) to test the front-end.

We write unit tests for particularly complex functions and components with a lot of internal logic.

We write integration tests for every page, covering all of the major flows.
- This includes various kinds of server responses, such as empty responses or server errors.
- This includes testing every user action that can be performed on the page.
- This includes testing navigation to other pages via links.

We also testing loading states in our test coverage. We do this reliably by using a deferred promise pattern. See below for an example where we defer the getUsers API endpoint to test the loading state.

```
export function defer() {
  let resolve, reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

// Create a variable to hold the deferred promise for the specific request
let deferGetUsers;

// Setup the MSW server
const server = setupServer(
  rest.get('/api/users', async (req, res, ctx) => {
    // 1. Await the deferred promise here
    await deferGetUsers.promise;

    // 2. Once the promise is resolved (in the test), send the final response
    return res(
      ctx.json([{ id: 1, name: 'Ava' }])
    );
  })
);

test('should show loading, then final data after delay', async () => {
  deferGetUsers = defer();
  render(<MyComponent />);

  const button = screen.getByRole('button', { name: /fetch users/i });

  // ACT: Click the button to start the network request
  fireEvent.click(button);

  // ASSERT: Verify Loading State
  // The request has been made but is currently "paused" by deferGetUsers.promise
  expect(screen.getByText(/loading.../i)).toBeInTheDocument();

  // ACT: Resolve the Promise to unblock the request
  // This is the step that allows the request to "go through"
  deferGetUsers.resolve();

  // ASSERT: Verify Final State
  // waitFor() waits for the deferGetUsers promise to resolve, the component to update,
  // and then checks for the final data.
  await waitFor(() => {
    expect(screen.getByText('Ava')).toBeInTheDocument();
  });
}
```
