/**
 * API response formatting utilities
 */

import { Response } from 'express';
import { ApiResponse, PaginatedResponse } from '../types';

const API_VERSION = process.env.API_VERSION || 'v1';

/**
 * Send a successful API response
 */
export function sendSuccess<T>(
  res: Response,
  data: T,
  statusCode: number = 200,
  meta?: Record<string, any>
): void {
  const response: ApiResponse<T> = {
    success: true,
    data,
    meta: {
      timestamp: new Date().toISOString(),
      version: API_VERSION,
      ...meta,
    },
  };

  res.status(statusCode).json(response);
}

/**
 * Send a paginated response
 */
export function sendPaginated<T>(
  res: Response,
  data: T[],
  pagination: {
    page: number;
    limit: number;
    total: number;
  }
): void {
  const pages = Math.ceil(pagination.total / pagination.limit);

  const response: PaginatedResponse<T> = {
    data,
    pagination: {
      page: pagination.page,
      limit: pagination.limit,
      total: pagination.total,
      pages,
      has_next: pagination.page < pages,
      has_prev: pagination.page > 1,
    },
  };

  sendSuccess(res, response);
}

/**
 * Send an error response
 */
export function sendError(
  res: Response,
  code: string,
  message: string,
  statusCode: number = 500,
  details?: Record<string, any>
): void {
  const response: ApiResponse = {
    success: false,
    error: {
      code,
      message,
      details,
    },
    meta: {
      timestamp: new Date().toISOString(),
      version: API_VERSION,
    },
  };

  res.status(statusCode).json(response);
}
