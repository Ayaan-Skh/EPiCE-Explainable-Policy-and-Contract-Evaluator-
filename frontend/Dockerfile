# syntax=docker/dockerfile:1

# ---- Build stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# NEXT_PUBLIC_* variables are inlined into the client bundle at BUILD time,
# so the API URL must be provided as a build arg (setting it at runtime has
# no effect on the browser bundle). Defaults to the local compose API.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

# Install dependencies against the lockfile for reproducible builds
COPY package.json package-lock.json ./
RUN npm ci

# Build the app (produces .next/standalone thanks to output: "standalone")
COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Run as an unprivileged user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy the minimal standalone server, static assets, and public files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# The standalone build emits server.js at the app root
CMD ["node", "server.js"]
