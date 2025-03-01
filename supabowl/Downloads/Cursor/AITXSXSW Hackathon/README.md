# Event Sonar - SXSW Event Browser

This project integrates the Event Harmony Browser frontend with a backend system for the SXSW Hackathon.

## Project Structure

- `/frontend` - Event Harmony Browser frontend built with React, TypeScript, and Tailwind CSS
- `/backend` - Backend services for Event Sonar

## Frontend

The frontend is based on the [event-harmony-browser](https://github.com/jhillbht/event-harmony-browser.git) project, which provides a user interface for browsing SXSW events with the following features:

- Event filtering and searching
- Event categorization by tags
- Microphone interface for voice commands
- Responsive design

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

This will start the development server at http://localhost:5173/

### Building for Production

```bash
cd frontend
npm run build
```

## Jordaaan Branch

This branch adds the Event Harmony Browser frontend to the project.

## Development Notes

- The frontend uses Vite for the build system
- UI components are built with shadcn/ui
- Styling is done with Tailwind CSS
- TypeScript is used for type safety

## License

See the LICENSE file for details.
