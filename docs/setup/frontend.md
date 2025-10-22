# Steps to set up an initial front-end

Create a new directory named frontend in the root folder. The entire frontend should be in the frontend folder.

### NextJS
Install NextJS inside the root folder. Note that node and nvm are already installed locally. Use Node 24.7.0. Please use a subdirectory named "src" inside of "frontend" as the root directory for the NextJS project.

### Shadcn UI
Install and use shadcn for the component library. Use shadcn whenever appropriate, for example for buttons or layout elements.

This will require you to install tailwindcss. Please also install "@tailwindcss/typography".

### Type-checking
Install typescript.

In package.json, add a script named "type-check": "tsc --noEmit".

Add a TypeScript declaration file at src/types/css.d.ts that tells TypeScript that importing a .css file returns void.

### Prettier
Install prettier for automatic code formatting. Also install eslint-config-prettier and eslint-plugin-prettier.
In eslint.config.mjs, extend "plugin:prettier/recommended".

Add a .prettierrc with:
{
  "semi": false,
  "trailingComma": "none",
  "singleQuote": true
}

### Testing

Please install Jest with React Testing Library (RTL) and Mock Servier Worker (MSW) for testing.
