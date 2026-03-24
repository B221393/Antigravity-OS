import time
import random
import math
import sys

# --- UTILITIES ---

def is_prime_miller_rabin(n, k=5):
    """Miller-Rabin primality test."""
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(digits=10):
    """Generates a random prime number with roughly `digits` digits."""
    start = 10**(digits-1)
    end = 10**digits - 1
    while True:
        cand = random.randint(start, end)
        if cand % 2 == 0: continue
        if is_prime_miller_rabin(cand):
            return cand

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# --- ALGORITHMS ---

def algo_trial_division_bounded(n, limit=1000000):
    """
    Naive Trial Division.
    Only runs up to `limit` iterations to prevent freezing on large numbers.
    Returns factor if found, else None.
    """
    if n % 2 == 0: return 2
    step = 0
    t_start = time.perf_counter()
    i = 3
    while i * i <= n:
        if n % i == 0:
            return i
        i += 2
        step += 1
        if step > limit:
            return None # Gave up
    return n

def algo_pollards_rho(n):
    """
    Pollard's Rho Algorithm.
    A probabilistic algorithm that is very effective for finding small factors.
    """
    if n % 2 == 0: return 2
    
    x = 2
    y = 2
    d = 1
    f = lambda x: (x * x + 1) % n
    
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
        
    if d == n:
        return None # Failed
    return d

def algo_pollards_rho_brent(n):
    """
    Pollard's Rho with Brent's Cycle Finding optimization.
    Generally faster than the standard Floyd's cycle-finding.
    """
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    
    y = random.randint(1, n - 1)
    c = random.randint(1, n - 1)
    m = random.randint(1, n - 1)
    g = 1
    r = 1
    q = 1
    
    xs = y
    x = y
    
    while g == 1:
        x = y
        for _ in range(r):
            y = (y*y + c) % n
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r - k)):
                y = (y*y + c) % n
                q = (q * abs(x - y)) % n
            g = gcd(q, n)
            k += m
        r *= 2
        
    if g == n:
        while True:
            xs = (xs*xs + c) % n
            g = gcd(abs(xs - y), n)
            if g > 1:
                break
                
    if g == n: return None
    return g

def algo_gravity_descent_3d(n):
    """
    Experimental: 'Gravity Well' Descent.
    Treats factorization as finding the global minimum of a 3D surface Z = (x*y - n)^2.
    Particles 'roll' down the gradient towards the solution.
    """
    if n % 2 == 0: return 2
    
    # Start mainly around sqrt(n), scattered slightly
    target = math.isqrt(n)
    
    # Spawn multiple "particles" (parallel attempts)
    particles = []
    for _ in range(5): 
        # Spread particles in a range [sqrt(n)/2, sqrt(n)*1.5]
        # We try to guess one factor 'x'. 'y' is derived or independent.
        start_x = random.randint(target // 2, target + target // 2)
        particles.append(float(start_x))
        
    learning_rate = 0.001
    
    # Physics Loop
    max_steps = 2000 
    
    for _ in range(max_steps):
        for i in range(len(particles)):
            x = particles[i]
            if x <= 1: x = 2.0
            
            # We assume y = n / x roughly, but we want to minimize error.
            # actually gradient descent on f(x) = (x * round(n/x) - n)^2 is bumpy.
            # Let's try flexible x, y approach or simply:
            # We want x such that x splits n.
            # Let's use f(x) = (n % x)^2 ? No, that's discrete.
            
            # Better 3D manifold: Let y = n / x. 
            # If x is a factor, y is an integer.
            # We want to minimize distance_to_integer(n/x).
            # Cost = (n/x - round(n/x))^2
            
            val = n / x
            nearest_int = round(val)
            diff = val - nearest_int
            
            # If extremely close to integer
            if abs(diff) < 1e-6:
                potential_factor = round(x)
                if potential_factor > 1 and n % potential_factor == 0:
                    return potential_factor
            
            # Gradient: d/dx (n/x - round(n/x))^2 
            # = 2 * (n/x - I) * ( -n/x^2 )
            # This pulls x towards a value where n/x is integer.
            
            grad = 2 * diff * (-n / (x*x))
            
            # Update position (gravity)
            # Dynamic learning rate helps convergence
            x = x - (learning_rate * grad * x) # Scale by x to move faster at large numbers
            particles[i] = x
            
            # Random "Thermal Noise" to jump out of local minima
            if random.random() < 0.1:
                particles[i] += random.choice([-1, 1]) * random.random()

    return None

def algo_particle_swarm(n):
    """
    Bio-inspired: Particle Swarm Optimization (PSO).
    A swarm of particles flies through the number space.
    They are attracted to "Integer Division Spots" (where n % x == 0).
    """
    if n % 2 == 0: return 2
    
    num_particles = 20
    target_root = math.isqrt(n)
    
    # Initialize Swarm
    # Position: x, Velocity: v, Best Pos: pbest, Best Score: pbest_score
    particles = []
    
    for _ in range(num_particles):
        x = random.randint(2, target_root * 2)
        particles.append({
            'x': float(x),
            'v': random.uniform(-100, 100),
            'pbest': float(x),
            'pbest_score': 1.0 # 1.0 is bad, 0.0 is perfect
        })
        
    gbest = particles[0]['x']
    gbest_score = 1.0
    
    # PSO Parameters
    w = 0.5   # Inertia
    c1 = 1.5  # Cognitive (memory)
    c2 = 1.5  # Social (swarm influence)
    
    steps = 1000
    
    for _ in range(steps):
        for p in particles:
            # Evaluate Fitness (How close is n/x to an integer?)
            # We avoid x=0 or x=1
            curr_x = p['x']
            if curr_x < 2: curr_x = 2.0
            
            val = n / curr_x
            diff = abs(val - round(val)) # The "Remainder Error"
            
            # Check for success
            if diff < 1e-7:
                candidate = int(round(curr_x))
                if candidate > 1 and n % candidate == 0:
                    return candidate
            
            # Update Personal Best
            if diff < p['pbest_score']:
                p['pbest_score'] = diff
                p['pbest'] = curr_x
            
            # Update Global Best
            if diff < gbest_score:
                gbest_score = diff
                gbest = curr_x
                
        # Move Particles
        for p in particles:
            r1 = random.random()
            r2 = random.random()
            
            # Velocity Update
            p['v'] = (w * p['v']) + \
                     (c1 * r1 * (p['pbest'] - p['x'])) + \
                     (c2 * r2 * (gbest - p['x']))
            
            # Position Update
            p['x'] += p['v']
            
            # Boundary constrain (simple reflection or reset)
            if p['x'] < 2: p['x'] = 2 + random.random()
            
    return None

def algo_particle_swarm_quantum(n):
    """
    Bio-inspired V2: Quantum Particle Swarm.
    - Uses GCD checks (Euclidean magic) on particles (stronger than division).
    - Implements 'Quantum Tunneling' to escape local loops.
    - Adaptive inertia for convergence.
    """
    if n % 2 == 0: return 2
    
    num_particles = 30
    target_root = math.isqrt(n)
    
    # Heuristic: limit search space if we assume factors are somewhat balanced
    # We search in [2, sqrt(n)]
    
    particles = []
    
    for _ in range(num_particles):
        x = random.randint(2, target_root)
        particles.append({
            'x': float(x),
            'v': random.uniform(-1, 1),
            'pbest': float(x),
            'pbest_score': 1.0, 
            'stagnation': 0
        })
        
    gbest = particles[0]['x']
    gbest_score = 1.0 # Minimize this (distance to integer division)
    
    # PSO Parameters
    w_max = 0.9
    w_min = 0.4
    c1 = 2.0
    c2 = 2.0
    
    steps = 3000
    
    for step in range(steps):
        # Adaptive Inertia
        w = w_max - ((w_max - w_min) * step / steps)
        
        # Check if we are stuck (Quantum Tunneling trigger)
        stuck_counter = 0
        
        for p in particles:
            curr_x = p['x']
            if curr_x < 2: curr_x = 2.0
            
            # --- THE MAGIC TRIGGER ---
            # Instead of just checking n % x == 0, check GCD.
            # If x is "close" to a factor factor*k, gcd(round(x), n) might reveal it.
            val_int = int(round(curr_x))
            if val_int > 1:
                # Fast GCD check
                if val_int == n: continue
                # We only check GCD occasionally to save time, or if 'close'
                common = gcd(val_int, n)
                if common > 1 and common < n:
                    return common
            
            # Fitness calculation (same as V1)
            val = n / curr_x
            diff = abs(val - round(val))
            
            if diff < p['pbest_score']:
                p['pbest_score'] = diff
                p['pbest'] = curr_x
            else:
                p['stagnation'] += 1
                
            if diff < gbest_score:
                gbest_score = diff
                gbest = curr_x
                
            # Quantum Tunneling (Teleport if stagnant)
            if p['stagnation'] > 50:
                p['x'] = random.randint(2, target_root)
                p['stagnation'] = 0
                stuck_counter += 1
                
        # Move
        for p in particles:
            r1 = random.random()
            r2 = random.random()
            
            p['v'] = (w * p['v']) + \
                     (c1 * r1 * (p['pbest'] - p['x'])) + \
                     (c2 * r2 * (gbest - p['x']))
            p['x'] += p['v']
            
            # Bound handling
            if p['x'] < 2: p['x'] = 2.0
            if p['x'] > n: p['x'] = float(target_root) # Reset
            
        # Large scale swarm teleport if everyone is stuck
        if stuck_counter > num_particles * 0.8:
             # Supernovas: scatter everyone
             for p in particles:
                 p['x'] = random.randint(2, target_root)
                 p['v'] = random.uniform(-50, 50)
    
    return None

def algo_genetic_evolution(n):
    """
    Bio-inspired: Genetic Algorithm (GA).
    Evolves a population of numbers to minimize the remainder of division.
    """
    if n % 2 == 0: return 2
    
    pop_size = 50
    generations = 500
    mutation_rate = 0.2
    
    # Initial Population (Concentrated around sqrt(n))
    root = math.isqrt(n)
    population = [random.randint(2, root * 2) for _ in range(pop_size)]
    
    for gen in range(generations):
        # 1. Evaluate Fitness (Lower remainder is better)
        # We want to minimize (n % x) OR (x - (n % x)) -> distance to nearest multiple
        scores = []
        for x in population:
            if x <= 1: x = 2
            rem = n % x
            fitness = min(rem, x - rem) # Distance to nearest divisor
            
            if fitness == 0:
                return x # Found it!
            
            scores.append((fitness, x))
            
        # 2. Selection (Survival of the fittest)
        scores.sort(key=lambda item: item[0])
        survivors = [s[1] for s in scores[:pop_size//2]] # Keep top 50%
        
        # 3. Crossover & Mutation
        next_gen = survivors[:]
        while len(next_gen) < pop_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            
            # Crossover: Average
            child = (parent1 + parent2) // 2
            
            # Mutation: Jitter
            if random.random() < mutation_rate:
                jitter = int(random.gauss(0, root * 0.1)) # Gaussian jitter
                child += jitter
            
            if child < 2: child = 2
            next_gen.append(child)
            
        population = next_gen
        
    return None

def algo_fermat_factorization(n):
    """
    Fermat's Factorization Method.
    Represent N as a difference of squares: N = a^2 - b^2 = (a-b)(a+b).
    Very fast if factors are close to sqrt(N).
    """
    if n % 2 == 0: return 2
    
    a = math.ceil(math.isqrt(n))
    b2 = a*a - n
    
    step = 0
    max_steps = 1000000 # Safety break
    
    while not math.isqrt(b2)**2 == b2:
        a += 1
        b2 = a*a - n
        step += 1
        if step > max_steps:
            return None
            
    b = math.isqrt(b2)
    return a - b

# --- BENCHMARK ENGINE ---

def run_arena(digits=10):
    print(f"\n[ FACTORIZATION ARENA - SETTING UP ]")
    print(f"Generating two random {digits}-digit primes...")
    
    t0 = time.time()
    p = generate_large_prime(digits)
    q = generate_large_prime(digits)
    N = p * q
    t_gen = time.time() - t0
    
    print(f"Target Acquired (Generation took {t_gen:.4f}s)")
    print(f"SECRET P: {p}")
    print(f"SECRET Q: {q}")
    print(f"TARGET N: {N} (approx {len(str(N))} digits)")
    print("-" * 50)
    
    # List of fighters
    fighters = [
        ("Pollard's Rho (Standard)", algo_pollards_rho),
        ("Pollard's Rho (Brent)", algo_pollards_rho_brent),
        ("Particle Swarm (Bio V1)", algo_particle_swarm),
        ("Quantum Swarm (Bio V2)", algo_particle_swarm_quantum),
        ("Genetic Evolution (Bio)", algo_genetic_evolution),
        ("Gravity Descent 3D (Exp)", algo_gravity_descent_3d),
        ("Fermat's Squares", algo_fermat_factorization)
    ]
    
    results = []
    
    for name, func in fighters:
        print(f"Running: {name}...")
        start_time = time.perf_counter()
        try:
            factor = func(N)
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            success = factor is not None and factor != 1 and factor != N and (N % factor == 0)
            
            res_str = f"Found {factor}" if success else "FAILED / TIMEOUT"
            print(f"  -> Result: {res_str}")
            print(f"  -> Time  : {duration:.6f} sec")
            results.append((name, duration, success))
            
        except Exception as e:
            print(f"  -> CRASHED: {e}")
            results.append((name, 0, False))
        print("-" * 20)

    # Summary
    print("\n[ ARENA RESULTS ]")
    results.sort(key=lambda x: x[1]) # Sort by time
    for rank, (name, duration, success) in enumerate(results, 1):
        status = "✅ CLEAN KILL" if success else "❌ FAILED"
        print(f"{rank}. {name:<25} | {duration:.6f}s | {status}")

if __name__ == "__main__":
    # If run directly
    digits = 10
    if len(sys.argv) > 1:
        digits = int(sys.argv[1])
    run_arena(digits)
