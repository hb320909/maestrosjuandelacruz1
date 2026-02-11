# Portal de Residencia Escolar MJC

## Overview
A school residence management portal (Portal de Residencia Escolar) for "Maestro Juan De La Cruz" in Albox. Built with vanilla JavaScript, Vite, and Tailwind CSS. Uses Supabase as the backend database for students, absences, and reports.

## Project Architecture
- **Frontend**: Vanilla JS + Tailwind CSS (via CDN) + Vite dev server
- **Backend**: Supabase (external service) for data persistence
- **Entry Point**: `index.html` loads `app.js` as an ES module
- **Styles**: `styles.css` for custom styles, Tailwind via CDN for utility classes

### Key Files
- `index.html` - Main HTML with all UI sections
- `app.js` - All application logic (login, CRUD, rooms, absences, reports, agenda)
- `styles.css` - Custom CSS enhancements
- `vite.config.js` - Vite configuration (port 5000, all hosts allowed)
- `supabase/schema.sql` - Database schema reference

### Features
- Teacher login system (hardcoded credentials)
- Student management (CRUD)
- Room assignment with bed tracking
- Absence tracking
- Report/incident management
- Academic follow-up (seguimiento)
- Homework agenda
- Birthday celebrations

## Development
- Dev server: `npm run dev` (Vite on port 5000)
- Build: `npm run build` (outputs to `dist/`)
- Deployment: Static site from `dist/` directory

## Recent Changes
- Configured for Replit environment (port 5000, allowed hosts)
- Fixed index.html to reference source files for dev mode
- Added missing `rooms` and `seguimientos` variable declarations
- Added `saveData()` function for localStorage persistence
- Exposed module functions to window for inline onclick handlers
