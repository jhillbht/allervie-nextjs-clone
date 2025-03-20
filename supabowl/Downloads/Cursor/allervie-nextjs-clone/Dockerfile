FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy app files
COPY . .

# Build the app
ENV NODE_ENV=production
RUN npm run build

# Runtime configuration
ENV PORT 8080
ENV HOSTNAME "0.0.0.0"
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/health || exit 1

# Start the app
CMD ["npm", "start"]