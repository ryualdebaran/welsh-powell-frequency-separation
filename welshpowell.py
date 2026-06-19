"""
    - Vertex            = instrument
    - Edge              = two instruments have characteristic frequency peaks
                          within one-third octave of each other (a conflict)
    - Color             = a frequency-compatible group
    - Chromatic number  = minimum number of such groups (approximated by
                          Welsh-Powell)

Frequency data: "Magic Frequencies" reference table
(Bobby Owsinski, The Mixing Engineer's Handbook).
"""

from collections import defaultdict


# ----------------------------------------------------------------------
# 1. DATA: characteristic frequency peaks (Hz) per instrument
#    Ranges in the source are reduced to their midpoint, e.g.
#    "bottom at 50 to 80 Hz" -> 65 Hz.
# ----------------------------------------------------------------------
INSTRUMENTS = {
    "Bass guitar":        [65, 700, 2500],
    "Kick drum":          [90, 400, 4000],
    "Snare":              [180, 900, 5000, 10000],
    "Toms":               [370, 6000],
    "Floor tom":          [80, 5000],
    "Hi-hat and cymbals": [200, 9000],
    "Electric guitar":    [370, 2000],
    "Acoustic guitar":    [80, 240, 3500],
    "Organ":              [80, 240, 3500],
    "Piano":              [80, 2500, 4000],
    "Horns":              [120, 5000],
    "Voice":              [120, 240, 5000, 5500, 12500],
    "Strings":            [240, 8500],
    "Conga":              [200, 5000],
}

# One-third octave ratio. An octave is a doubling (ratio 2.0), so a third of an
# octave is 2 ** (1/3) ~= 1.26. Two peaks are "in conflict" when the ratio of
# the higher to the lower is at most this value.
THIRD_OCTAVE = 2 ** (1 / 3)   

def conflicts(peaks_a, peaks_b, tol=THIRD_OCTAVE):
    for fa in peaks_a:
        for fb in peaks_b:
            if max(fa, fb) / min(fa, fb) <= tol:
                return True
    return False



# 3. BUILD  GRAPH (as an adjacency list)
def build_graph(instruments):
    """Return adjacency list {instrument: set(conflicting instruments)}."""
    graph = defaultdict(set)
    names = list(instruments)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if conflicts(instruments[a], instruments[b]):
                graph[a].add(b)
                graph[b].add(a)
    for name in names:
        _ = graph[name]
    return graph



# 4. WELSH-POWELL COLORING
def welsh_powell(graph, vertices, verbose=False):
    """Greedy graph coloring, processing vertices by descending degree.

    Returns {vertex: color} where color is a positive integer (group number).
    If verbose=True, prints the algorithm's reasoning at every step.
    """
    
    order = sorted(vertices, key=lambda v: len(graph[v]), reverse=True)

    if verbose:
        print("=" * 70)
        print("WELSH-POWELL EXECUTION (step by step)")
        print("=" * 70)
        print("Step 1 - sort vertices by descending degree:")
        print("" + "\n".join(f"{v} ({len(graph[v])})" for v in order))
        print("\nStep 2 - assign each vertex the lowest color not used by a")
        print("         neighbor, in the order above:\n")

    color = {}
    for step, v in enumerate(order, 1):
        # colors already taken by this vertex's already-colored neighbors
        colored_neighbors = {u: color[u] for u in graph[v] if u in color}
        used = set(colored_neighbors.values())

        # smallest positive color not in 'used'
        c = 1
        while c in used:
            c += 1
        color[v] = c

        if verbose:
            print(f"  [{step:>2d}] {v}  (degree {len(graph[v])})")
            if colored_neighbors:
                nb = ", ".join(f"{u}=C{cc}"
                               for u, cc in sorted(colored_neighbors.items(),
                                                   key=lambda kv: kv[1]))
                print(f"        already-colored neighbours: {nb}")
                print(f"        colors blocked: {sorted(used)}  ->  "
                      f"smallest free color = C{c}")
            else:
                print("        no colored neighbours yet  ->  takes C1")
            print(f"        ASSIGN -> Color {c}\n")

    if verbose:
        print(f"Total colors used: {max(color.values())}")
        print("=" * 70 + "\n")

    return color



# 5. HELPERS FOR REPORTING

def print_adjacency_list(graph, names):
    """Print the conflict graph as an adjacency list."""
    width = max(len(n) for n in names)
    for v in names:
        neighbors = sorted(graph[v], key=lambda u: names.index(u))
        deg = len(neighbors)
        if neighbors:
            print(f"  {v:<{width}s} (deg {deg:>2d}) -> {', '.join(neighbors)}")
        else:
            print(f"  {v:<{width}s} (deg {deg:>2d}) -> (no conflicts)")


def verify_coloring(graph, color):
    """Return True if no two adjacent vertices share a color."""
    for v in graph:
        for u in graph[v]:
            if color[v] == color[u]:
                return False
    return True


# 6. MAIN
def main():
    names = list(INSTRUMENTS)
    n = len(names)

    graph = build_graph(INSTRUMENTS)

    # stats
    degree = {v: len(graph[v]) for v in names}
    edges = sum(degree.values()) // 2
    density = edges / (n * (n - 1) / 2) * 100

    print("=" * 70)
    print("GRAPH STATISTICS")
    print("=" * 70)
    print(f"Vertices (instruments): {n}")
    print(f"Edges (conflicts):      {edges}")
    print(f"Density:                {density:.1f}%")
    print(f"Max degree:             {max(degree.values())}")
    print(f"Min degree:             {min(degree.values())}")

    # graph representation
    print("\n" + "=" * 70)
    print("GRAPH (adjacency list)")
    print("=" * 70)
    print_adjacency_list(graph, names)

    # Welsh-Powell, with full step-by-step trace
    print()
    coloring = welsh_powell(graph, names, verbose=True)

    # grouping result
    groups = defaultdict(list)
    for inst, c in coloring.items():
        groups[c].append(inst)

    print("=" * 70)
    print(f"RESULT: {len(groups)} GROUPS")
    print("=" * 70)
    for g in sorted(groups):
        print(f"Group {g}: {', '.join(groups[g])}")

    print("\nValid coloring (no group has an internal conflict):",
          verify_coloring(graph, coloring))
    print("\nNote: Welsh-Powell gives an UPPER BOUND on the chromatic number;")
    print(f"      {len(groups)} groups suffice, but may not be the proven minimum.")


if __name__ == "__main__":
    main()