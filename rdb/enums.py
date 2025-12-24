"""Database enumeration types.

This module defines all enum types used across the database schema.
"""

import enum


class OrderStatus(enum.Enum):
    """Order status enumeration.

    Attributes:
        PENDING: Order has been created but not yet processed.
        PROCESSING: Order is being prepared for shipment.
        SHIPPED: Order has been shipped to the customer.
        DELIVERED: Order has been successfully delivered.
        CANCELLED: Order has been cancelled.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
