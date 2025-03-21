FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the application
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
RUN npm run build

# Set environment variables
ENV PORT 8080
ENV HOSTNAME "0.0.0.0"

# Expose port
EXPOSE 8080

# Start the application
CMD ["npm", "start"]
