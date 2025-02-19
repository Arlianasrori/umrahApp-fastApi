from enum import Enum

class PackageTypeEnum(Enum) :
    SILVER = "SILVER"
    GOLD = "GOLD"
    PREMIUM = "PREMIUM"

class RoomTypeEnum(Enum) :
    QUAD = "QUAD"
    TRIPLE = "TRIPLE"
    DOUBLE = "DOUBLE" 

class BookingStatusEnum(Enum) :
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"