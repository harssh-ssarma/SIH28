FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (all deps for build, then prune in production)
RUN npm ci

# Copy source code
COPY . .

# Build for production (skip in development)
RUN if [ "$NODE_ENV" != "development" ] ; then SKIP_ENV_VALIDATION=1 npm run build ; fi

EXPOSE 3000

# Smart command selection
CMD if [ "$NODE_ENV" = "development" ] ; then npm run dev ; else npm start ; fi