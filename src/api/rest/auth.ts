/**
 * Authentication API routes
 */

import { Router, Request, Response, NextFunction } from 'express';
import { validate, CreateUserSchema } from '../../utils/validators';
import { hashPassword, verifyPassword, generateToken } from '../../utils/auth';
import { sendSuccess, sendError } from '../../utils/response';
import { AuthenticationError, ValidationError } from '../../utils/errors';
import postgres from '../../db/postgresql/connection';
import { logger } from '../../utils/logger';

const router = Router();

/**
 * POST /auth/register
 * Register a new user
 */
router.post('/register', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const data = validate(CreateUserSchema, req.body);

    // Check if email already exists
    const existing = await postgres.query('SELECT id FROM users WHERE email = $1', [data.email]);

    if (existing.rows.length > 0) {
      throw new ValidationError('Email already registered');
    }

    // Hash password
    const passwordHash = await hashPassword(data.password);

    // Create user
    const result = await postgres.query(
      `
      INSERT INTO users (email, password_hash, name, timezone)
      VALUES ($1, $2, $3, $4)
      RETURNING id, email, name, subscription_tier
    `,
      [data.email, passwordHash, data.name, data.timezone || 'UTC']
    );

    const user = result.rows[0];

    // Generate token
    const token = generateToken(user);

    logger.info('User registered', { userId: user.id, email: user.email });

    sendSuccess(res, { user, token }, 201);
  } catch (error) {
    next(error);
  }
});

/**
 * POST /auth/login
 * Login user
 */
router.post('/login', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      throw new ValidationError('Email and password required');
    }

    // Get user
    const result = await postgres.query(
      `
      SELECT id, email, password_hash, name, subscription_tier
      FROM users
      WHERE email = $1
    `,
      [email]
    );

    if (result.rows.length === 0) {
      throw new AuthenticationError('Invalid email or password');
    }

    const user = result.rows[0];

    // Verify password
    const valid = await verifyPassword(password, user.password_hash);

    if (!valid) {
      throw new AuthenticationError('Invalid email or password');
    }

    // Update last login
    await postgres.query('UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = $1', [
      user.id,
    ]);

    // Generate token
    const token = generateToken(user);

    logger.info('User logged in', { userId: user.id, email: user.email });

    sendSuccess(res, {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        subscription_tier: user.subscription_tier,
      },
      token,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /auth/me
 * Get current user
 */
router.get('/me', async (req: Request, res: Response, next: NextFunction) => {
  try {
    // This would use authenticate middleware in practice
    sendSuccess(res, { message: 'Not implemented yet' });
  } catch (error) {
    next(error);
  }
});

export default router;
