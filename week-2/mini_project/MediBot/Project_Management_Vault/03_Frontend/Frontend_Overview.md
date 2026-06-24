# Frontend Overview

The MediBot user interface is a Single Page Application (SPA) built using **React**. 

## Tech Stack
- **Framework**: React
- **Bundler**: Vite (Lightning fast development server and optimized production build)
- **Styling**: Tailwind CSS (Utility-first CSS framework)
- **Linting**: ESLint

## Directory Structure
- `src/`: The core application code. This is where React components, pages, custom hooks, and contexts live.
- `public/`: Static assets (like the favicon or external images) that are not processed by Vite.
- `dist/`: The production-ready folder generated after running `npm run build`.

## Configuration Files
- `package.json`: Lists the npm dependencies and scripts.
- `vite.config.js`: Configuration for the Vite bundler.
- `tailwind.config.js`: Defines the Tailwind design tokens, custom colors, and paths to scan for class names.
- `eslint.config.js`: Rules for code linting and formatting.

## Running the Frontend
To run the development server locally:
```bash
cd frontend
npm install # if not already installed
npm run dev
```
