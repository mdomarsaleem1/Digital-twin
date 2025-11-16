/**
 * PostgreSQL database connection and query utilities
 */

import { Pool, PoolClient, QueryResult } from 'pg';
import { logger } from '../../utils/logger';

class PostgreSQLConnection {
  private pool: Pool;
  private static instance: PostgreSQLConnection;

  private constructor() {
    this.pool = new Pool({
      host: process.env.POSTGRES_HOST || 'localhost',
      port: parseInt(process.env.POSTGRES_PORT || '5432'),
      database: process.env.POSTGRES_DB || 'knowledge_twin',
      user: process.env.POSTGRES_USER || 'postgres',
      password: process.env.POSTGRES_PASSWORD || 'postgres',
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    this.pool.on('error', (err) => {
      logger.error('Unexpected PostgreSQL pool error', { error: err });
    });

    this.pool.on('connect', () => {
      logger.info('New PostgreSQL connection established');
    });
  }

  public static getInstance(): PostgreSQLConnection {
    if (!PostgreSQLConnection.instance) {
      PostgreSQLConnection.instance = new PostgreSQLConnection();
    }
    return PostgreSQLConnection.instance;
  }

  /**
   * Execute a query with parameters
   */
  async query<T = any>(text: string, params?: any[]): Promise<QueryResult<T>> {
    const start = Date.now();
    try {
      const result = await this.pool.query<T>(text, params);
      const duration = Date.now() - start;

      logger.debug('Executed PostgreSQL query', {
        text,
        duration,
        rows: result.rowCount,
      });

      return result;
    } catch (error) {
      logger.error('PostgreSQL query error', { text, error });
      throw error;
    }
  }

  /**
   * Get a client from the pool for transactions
   */
  async getClient(): Promise<PoolClient> {
    return await this.pool.connect();
  }

  /**
   * Execute a transaction
   */
  async transaction<T>(callback: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.getClient();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      logger.error('Transaction rolled back', { error });
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Check database connection
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.query('SELECT 1');
      return true;
    } catch (error) {
      logger.error('PostgreSQL health check failed', { error });
      return false;
    }
  }

  /**
   * Close all connections
   */
  async close(): Promise<void> {
    await this.pool.end();
    logger.info('PostgreSQL pool closed');
  }
}

export const postgres = PostgreSQLConnection.getInstance();
export default postgres;
