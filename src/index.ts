/**
 * Digital Knowledge Twin Platform - Main Entry Point
 */

import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { logger } from './utils/logger';
import { errorHandler } from './api/middleware/errorHandler';
import postgres from './db/postgresql/connection';
import neo4jDB from './db/neo4j/connection';
import mongodb from './db/mongodb/connection';
import redis from './db/redis/connection';

// Import routes
import authRoutes from './api/rest/auth';

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

class Server {
  private app: Application;

  constructor() {
    this.app = express();
    this.configureMiddleware();
    this.configureRoutes();
    this.configureErrorHandling();
  }

  /**
   * Configure Express middleware
   */
  private configureMiddleware(): void {
    // Security middleware
    this.app.use(helmet());

    // CORS
    this.app.use(
      cors({
        origin: process.env.CORS_ORIGIN || '*',
        credentials: true,
      })
    );

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging
    this.app.use((req, res, next) => {
      logger.info('Incoming request', {
        method: req.method,
        path: req.path,
        ip: req.ip,
      });
      next();
    });
  }

  /**
   * Configure API routes
   */
  private configureRoutes(): void {
    const apiVersion = process.env.API_VERSION || 'v1';

    // Health check
    this.app.get('/health', async (req, res) => {
      const health = {
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: NODE_ENV,
        databases: {
          postgresql: await postgres.healthCheck(),
          neo4j: await neo4jDB.healthCheck(),
          mongodb: await mongodb.healthCheck(),
          redis: await redis.healthCheck(),
        },
      };

      const allHealthy = Object.values(health.databases).every((status) => status === true);

      res.status(allHealthy ? 200 : 503).json(health);
    });

    // API routes
    this.app.use(`/${apiVersion}/auth`, authRoutes);

    // TODO: Add more routes
    // this.app.use(`/${apiVersion}/users`, userRoutes);
    // this.app.use(`/${apiVersion}/goals`, goalRoutes);
    // this.app.use(`/${apiVersion}/learning-paths`, learningPathRoutes);
    // this.app.use(`/${apiVersion}/resources`, resourceRoutes);
    // this.app.use(`/${apiVersion}/skills`, skillRoutes);

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: `Route ${req.method} ${req.path} not found`,
        },
      });
    });
  }

  /**
   * Configure error handling
   */
  private configureErrorHandling(): void {
    this.app.use(errorHandler);
  }

  /**
   * Initialize database connections
   */
  private async initializeDatabases(): Promise<void> {
    try {
      logger.info('Connecting to databases...');

      // Connect to MongoDB
      await mongodb.connect();

      // Connect to Redis
      await redis.connect();

      // Test PostgreSQL connection
      const pgHealthy = await postgres.healthCheck();
      if (!pgHealthy) {
        throw new Error('PostgreSQL connection failed');
      }

      // Test Neo4j connection
      const neo4jHealthy = await neo4jDB.healthCheck();
      if (!neo4jHealthy) {
        throw new Error('Neo4j connection failed');
      }

      logger.info('All database connections established');
    } catch (error) {
      logger.error('Database initialization failed', { error });
      throw error;
    }
  }

  /**
   * Start the server
   */
  async start(): Promise<void> {
    try {
      // Initialize databases
      await this.initializeDatabases();

      // Start HTTP server
      this.app.listen(PORT, () => {
        logger.info(`Server started on port ${PORT}`, {
          environment: NODE_ENV,
          port: PORT,
        });
      });

      // Graceful shutdown
      this.setupGracefulShutdown();
    } catch (error) {
      logger.error('Failed to start server', { error });
      process.exit(1);
    }
  }

  /**
   * Setup graceful shutdown
   */
  private setupGracefulShutdown(): void {
    const shutdown = async (signal: string) => {
      logger.info(`${signal} received. Starting graceful shutdown...`);

      try {
        // Close database connections
        await postgres.close();
        await neo4jDB.close();
        await mongodb.close();
        await redis.close();

        logger.info('Graceful shutdown completed');
        process.exit(0);
      } catch (error) {
        logger.error('Error during shutdown', { error });
        process.exit(1);
      }
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));
  }
}

// Start the server
const server = new Server();
server.start();

export default server;
