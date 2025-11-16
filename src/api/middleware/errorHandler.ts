/**
 * Global error handling middleware
 */

import { Request, Response, NextFunction } from 'express';
import { KnowledgeTwinError } from '../../utils/errors';
import { sendError } from '../../utils/response';
import { logger } from '../../utils/logger';
import { ZodError } from 'zod';

export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  logger.error('Request error', {
    error: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
  });

  // Handle custom application errors
  if (error instanceof KnowledgeTwinError) {
    return sendError(res, error.code, error.message, error.statusCode, error.details);
  }

  // Handle Zod validation errors
  if (error instanceof ZodError) {
    return sendError(res, 'VALIDATION_ERROR', 'Invalid input data', 400, {
      errors: error.errors,
    });
  }

  // Handle other errors
  sendError(res, 'INTERNAL_SERVER_ERROR', 'An unexpected error occurred', 500);
};
