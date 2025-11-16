/**
 * Neo4j knowledge graph database connection
 */

import neo4j, { Driver, Session, Result, QueryResult } from 'neo4j-driver';
import { logger } from '../../utils/logger';

class Neo4jConnection {
  private driver: Driver;
  private static instance: Neo4jConnection;

  private constructor() {
    const uri = process.env.NEO4J_URI || 'bolt://localhost:7687';
    const user = process.env.NEO4J_USER || 'neo4j';
    const password = process.env.NEO4J_PASSWORD || 'neo4jpassword';

    this.driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {
      maxConnectionPoolSize: 50,
      connectionAcquisitionTimeout: 2000,
    });

    logger.info('Neo4j driver initialized');
  }

  public static getInstance(): Neo4jConnection {
    if (!Neo4jConnection.instance) {
      Neo4jConnection.instance = new Neo4jConnection();
    }
    return Neo4jConnection.instance;
  }

  /**
   * Get a new session
   */
  getSession(database?: string): Session {
    return this.driver.session({
      database: database || 'neo4j',
      defaultAccessMode: neo4j.session.READ,
    });
  }

  /**
   * Execute a read query
   */
  async read<T = any>(
    query: string,
    params?: Record<string, any>,
    database?: string
  ): Promise<T[]> {
    const session = this.getSession(database);
    const start = Date.now();

    try {
      const result = await session.run(query, params);
      const duration = Date.now() - start;

      logger.debug('Executed Neo4j read query', {
        query: query.substring(0, 100),
        duration,
        records: result.records.length,
      });

      return result.records.map((record) => record.toObject() as T);
    } catch (error) {
      logger.error('Neo4j read query error', { query, error });
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * Execute a write query
   */
  async write<T = any>(
    query: string,
    params?: Record<string, any>,
    database?: string
  ): Promise<T[]> {
    const session = this.driver.session({
      database: database || 'neo4j',
      defaultAccessMode: neo4j.session.WRITE,
    });
    const start = Date.now();

    try {
      const result = await session.run(query, params);
      const duration = Date.now() - start;

      logger.debug('Executed Neo4j write query', {
        query: query.substring(0, 100),
        duration,
        records: result.records.length,
      });

      return result.records.map((record) => record.toObject() as T);
    } catch (error) {
      logger.error('Neo4j write query error', { query, error });
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * Execute a transaction
   */
  async transaction<T>(
    callback: (tx: any) => Promise<T>,
    database?: string
  ): Promise<T> {
    const session = this.driver.session({
      database: database || 'neo4j',
      defaultAccessMode: neo4j.session.WRITE,
    });

    try {
      const result = await session.writeTransaction(callback);
      return result;
    } catch (error) {
      logger.error('Neo4j transaction error', { error });
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.read('RETURN 1');
      return true;
    } catch (error) {
      logger.error('Neo4j health check failed', { error });
      return false;
    }
  }

  /**
   * Close the driver
   */
  async close(): Promise<void> {
    await this.driver.close();
    logger.info('Neo4j driver closed');
  }
}

export const neo4jDB = Neo4jConnection.getInstance();
export default neo4jDB;
