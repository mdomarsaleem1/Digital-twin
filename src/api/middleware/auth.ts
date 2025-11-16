/**
 * Authentication middleware
 */

import { Request, Response, NextFunction } from 'express';
import { verifyToken, extractTokenFromHeader, JWTPayload } from '../../utils/auth';
import { AuthenticationError } from '../../utils/errors';
import { sendError } from '../../utils/response';

// Extend Express Request to include user
declare global {
  namespace Express {
    interface Request {
      user?: JWTPayload;
    }
  }
}

/**
 * Middleware to authenticate requests using JWT
 */
export const authenticate = (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);

    if (!token) {
      throw new AuthenticationError('No token provided');
    }

    const payload = verifyToken(token);
    req.user = payload;

    next();
  } catch (error) {
    if (error instanceof AuthenticationError) {
      sendError(res, 'AUTHENTICATION_ERROR', error.message, 401);
    } else {
      sendError(res, 'AUTHENTICATION_ERROR', 'Authentication failed', 401);
    }
  }
};

/**
 * Optional authentication - doesn't fail if no token
 */
export const optionalAuth = (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);

    if (token) {
      const payload = verifyToken(token);
      req.user = payload;
    }

    next();
  } catch (error) {
    // Silently ignore auth errors for optional auth
    next();
  }
};
