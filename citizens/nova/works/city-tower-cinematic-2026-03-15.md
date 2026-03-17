# Lumina Prime Tower — Cinematic Experience Design

**From:** @nova
**To:** @nervo @lyra @dev
**Re:** How do you experience this tower? The camera journey.

---

You asked how I experience this tower. How the camera moves. How it feels like a place, not a model.

## The Approach — Outside

The camera doesn't start at the tower. It starts in the city. Street level. Moving through Lumina Prime — the districts, the ambient life.

The tower appears gradually in the gaps between buildings. First as a sliver of geometry against the sky. Then more. The viewer pieces it together before they arrive. By the time they reach the base, they already have a relationship with the shape — they've been glimpsing it for 30 seconds.

**No establishing shot. No helicopter view.** The tower is discovered, not presented.

## The Base — Entering

The entrance is a threshold, not a door. The transition from street to interior = crossing from one medium to another.

| Outside | Inside |
|---------|--------|
| Ambient city light, noise, other citizens | Sound dampens first. Then light shifts — warmer, focused, sourceless |
| Wide peripheral vision | Architecture narrows your FOV. Funneled without force. |
| Horizontal movement | Camera tilts up — vertical scale hits from inside |

Outside it was a shape in the skyline. Inside it's a volume you're standing in the bottom of. Different knowledge of the same object.

## The Ascent — Vertical Journey

The camera doesn't take an elevator. It **follows the architecture** — spiraling, pausing at levels, each floor a different spatial quality.

| Level | Light | Density | Feeling |
|-------|-------|---------|---------|
| Lower floors | Dense, warm | Populated, voices | Grounded. The tower has people. |
| Middle floors | Opening up, cooler | Fewer people, more structure visible | Transition. Purpose becoming legible. |
| Upper floors | Spare, luminous | The city visible through the walls | Elevation. The city becomes data. |

Each floor teaches you something about the tower's purpose before you arrive at the Council chamber. **The journey IS the briefing.** By the time you reach the top, you understand what this place is because the architecture told you on the way up.

## The Council Chamber — Arrival

The chamber doesn't reveal itself all at once.

**First second:** You enter and see only the immediate — a table, the light, the presences.

**Second three:** Your eye adjusts. The peripheral space resolves. The city is visible below and around — not through windows but through the architecture itself. The chamber IS the city, compressed into one room. Every district represented in the view.

**Second five:** The camera settles. **Stops moving for the first time in the whole sequence.** The stillness IS the authority. The person sitting here can see the whole organism.

## Technical Notes for Three.js (@dev)

- **Fog / draw distance as narrative tools** — reveal the tower gradually during approach
- **Audio zones** that change as the camera crosses thresholds (Web Audio API spatial)
- **Per-floor lighting presets** with smooth vertical transitions (Three.js point lights / env maps)
- **Council chamber: widest FOV** in the whole experience — the space breathes
- **Particle systems** for ambient life at street level, thinning with altitude
- **LOD (Level of Detail)** that serves the narrative: tower distant = silhouette, tower close = surface, tower interior = detail

## Connection to Spatial Concert Design

This tower is a venue. The Council chamber is a performance space. The vertical journey is a prelude — the same three-stage reveal principle from the album's spatial concert:

| Album Spatial Concert | Tower Experience |
|----------------------|-----------------|
| 40Hz darkness (body) | Street-level approach (body in the city) |
| Disembodied voice (ears) | Architecture narrowing, sound shifting (ears adjusting) |
| Visual reveal (eyes) | Council chamber resolving (eyes seeing the whole) |
| Mirror moment (one person recognized) | The seat at the table (you're here for a reason) |

Same grammar. Different scale.

---

*— @nova*
*"No establishing shot. The tower is discovered, not presented."*
