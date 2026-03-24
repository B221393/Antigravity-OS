export interface PhysicsResult {
    time: number;
    distance: number;
    velocity: number;
}

export class AnimePhysics {
    static GRAVITY = 9.80665;
    static AIR_DENSITY = 1.225; // kg/m^3

    /**
     * Calculates free fall distance given time and gravity multiplier.
     * Useful for scaling based on how long a character takes to fall.
     */
    static calculateFall(time: number, gMultiplier: number = 1): PhysicsResult {
        const g = this.GRAVITY * gMultiplier;
        const distance = 0.5 * g * Math.pow(time, 2);
        const velocity = g * time;
        return { time, distance, velocity };
    }

    /**
     * Calculates drag force and terminal velocity.
     * Fd = 1/2 * rho * v^2 * Cd * A
     */
    static calculateTerminalVelocity(mass: number, area: number, dragCoefficient: number = 0.47): number {
        return Math.sqrt((2 * mass * this.GRAVITY) / (this.AIR_DENSITY * area * dragCoefficient));
    }

    /**
     * Centrifugal force F = mv^2 / r
     */
    static calculateCentrifugalForce(mass: number, velocity: number, radius: number): number {
        return (mass * Math.pow(velocity, 2)) / radius;
    }

    /**
     * Scaling utility to convert pixel measurements to real meters.
     * @param referencePixels Number of pixels for a known height.
     * @param referenceMeters Real height in meters.
     * @param targetPixels Number of pixels to convert.
     */
    static pixelsToMeters(referencePixels: number, referenceMeters: number, targetPixels: number): number {
        const metersPerPixel = referenceMeters / referencePixels;
        return targetPixels * metersPerPixel;
    }
}
