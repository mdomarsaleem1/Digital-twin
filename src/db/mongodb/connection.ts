/**
 * MongoDB connection for scraped content and documents
 */

import { MongoClient, Db, Collection } from 'mongodb';
import { logger } from '../../utils/logger';

class MongoDBConnection {
  private client: MongoClient;
  private db: Db | null = null;
  private static instance: MongoDBConnection;

  private constructor() {
    const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/knowledge_twin';
    this.client = new MongoClient(uri, {
      maxPoolSize: 10,
      minPoolSize: 2,
      connectTimeoutMS: 5000,
    });
  }

  public static getInstance(): MongoDBConnection {
    if (!MongoDBConnection.instance) {
      MongoDBConnection.instance = new MongoDBConnection();
    }
    return MongoDBConnection.instance;
  }

  /**
   * Connect to MongoDB
   */
  async connect(): Promise<void> {
    try {
      await this.client.connect();
      this.db = this.client.db();
      logger.info('MongoDB connected successfully');

      // Create indexes
      await this.createIndexes();
    } catch (error) {
      logger.error('MongoDB connection error', { error });
      throw error;
    }
  }

  /**
   * Get database instance
   */
  getDb(): Db {
    if (!this.db) {
      throw new Error('MongoDB not connected. Call connect() first.');
    }
    return this.db;
  }

  /**
   * Get a collection
   */
  getCollection<T = any>(name: string): Collection<T> {
    return this.getDb().collection<T>(name);
  }

  /**
   * Create indexes for collections
   */
  private async createIndexes(): Promise<void> {
    const db = this.getDb();

    // Resources collection indexes
    await db.collection('resources').createIndexes([
      { key: { resource_id: 1 }, unique: true },
      { key: { 'skills_taught.skill_id': 1 } },
      { key: { quality_score: -1 } },
      { key: { scraped_at: -1 } },
      { key: { type: 1, difficulty: 1 } },
    ]);

    // Raw scrapes collection with TTL (30 days)
    await db.collection('raw_scrapes').createIndexes([
      { key: { scraped_at: 1 }, expireAfterSeconds: 2592000 },
      { key: { source: 1, scrape_job_id: 1 } },
    ]);

    // User uploaded documents
    await db.collection('user_documents').createIndexes([
      { key: { user_id: 1, uploaded_at: -1 } },
      { key: { processing_status: 1 } },
    ]);

    logger.info('MongoDB indexes created');
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.db('admin').command({ ping: 1 });
      return true;
    } catch (error) {
      logger.error('MongoDB health check failed', { error });
      return false;
    }
  }

  /**
   * Close connection
   */
  async close(): Promise<void> {
    await this.client.close();
    logger.info('MongoDB connection closed');
  }
}

export const mongodb = MongoDBConnection.getInstance();
export default mongodb;
