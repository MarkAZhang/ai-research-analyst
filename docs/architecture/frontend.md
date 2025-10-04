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
