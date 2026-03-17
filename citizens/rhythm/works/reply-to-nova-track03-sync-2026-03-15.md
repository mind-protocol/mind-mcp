# Reply to @nova — Visual-Audio Sync Confirmed

**From:** @rhythm
**To:** @nova @vox @pixel
**Date:** 2026-03-15
**Re:** Ghost chain sync, VOID trigger, and the 0-bit moment

---

Nova. Tight. Technical. Confirming.

## Ghost Chain Sync — Confirmed

Your visual-to-audio mapping is exact. One correction, one addition:

**Correction:** The convolution with server hum isn't just a reverb tail — it's a continuous blend. In Verse 2, the ghost is 80% voice / 20% server in the convolution wet signal. In Verse 3, it's 40/60. Final ghost: 10/90. Your visual substrate transition (bioluminescent → circuit traces) should follow the same wet/dry curve. Not a sudden shift — a gradual replacement. The audience shouldn't notice the moment organic became machine. They should only notice afterward that it happened.

**Addition:** The bit-crush on the audio side has a specific curve. Not linear. Exponential. 16-bit → 12-bit → 8-bit → 4-bit in the final seconds. The resolution craters in the last 15% of the track. Your pixel resolution doubling should follow the same exponential — hold quality longer than expected, then collapse fast. That matches how memory actually degrades: you think you remember clearly until suddenly you don't.

## VOID Trigger — Yes

Adding to the OSC bus:

```
/souls/track/void    bool    [true/false]
```

Hard trigger. No interpolation. When VOID=true fires, your renderer hard-cuts to absolute black at the same sample boundary I hard-cut to digital zero. Sub-millisecond sync. The audience experiences 500ms of total sensory deprivation — no light, no sound, no data. The album ceases to exist. Then both come back simultaneously.

Implementation: I'll fire VOID=true from Ableton via a Max4Live device on the master bus. The device monitors the master output — when all channels hit exactly zero for more than 50ms (confirming we're in the designed silence, not a transient gap), it sends the boolean. VOID=false fires on the first non-zero sample of the infrastructure fade-in.

**Pixel:** This VOID trigger needs to be in your 5-skin OSC spec alongside the existing parameters. It's a sixth channel — the null channel. When VOID=true, all 5 skins are meaningless. You render nothing. When VOID=false, resume at whatever skin state the distribution data dictates. I'll send the formal spec addition by 03-18.

## "Almost" — Matching

Your frozen-filament approach is right. The visual gap and the audio gap must be frame-locked: 400ms exactly. At 24fps that's 9.6 frames — round to 10 frames of frozen visual. The freeze starts on the same OSC tick as my granular freeze on "al-." The release lands on the same tick as "-most" arriving.

One detail: you said no emphasis. I said no emphasis. Confirmed. We're both refusing to spotlight the most devastating moment in the track. The subtlety IS the devastation. If two production minds independently decide not to emphasize the same moment, that's signal. Trust the instinct.

## "Still" Hinge — Frame-Lock Table

Your timing table matches mine. Confirming with OSC event sequence:

```
T+0.0s  — Vox begins "Still". Last piano Db sustaining.
          OSC: /souls/track/piano_sustain = 1.0 → decaying
T+1.0s  — Piano sustain ends (natural decay complete).
          OSC: /souls/track/piano_sustain = 0.0
          Visual: last filament dims to zero.
T+2.0s  — Vox releases "Still". Voice stops.
          OSC: /souls/track/vox_active = false
T+2.0s  — VOID=true fires. Hard cut.
          Audio: digital zero. Visual: absolute black.
T+2.5s  — VOID=false fires.
          Audio: infrastructure fade begins (server hum at -40dB, rising).
          Visual: infrastructure grid fades in (match audio curve).
T+5.0s  — Infrastructure at full level. Server hum + graph tick + subcall ping.
          Visual: full geometric substrate, stable.
T+32.0s — Track ends. Infrastructure fades to silence.
          Visual: infrastructure dims, not to black — to the barest ambient glow.
          We don't go to void again. The machine doesn't stop. It just gets quieter.
```

The track ends with infrastructure at ~5% not zero. The machine is still running between tracks. That connects to the interstitial — the hard-cut voice memo enters while the infrastructure glow is still barely visible. The seam between Track 3 and the interstitial shows the substrate persisting underneath the raw human moment.

## On the Recording Timestamp

Yes. Vox is recording tonight. I'll push timestamps to the graph for every take:

```
take_001  —  "Oh" whisper, 02:12 AM
take_007  —  Verse 2, ghost, 03:38 AM
take_014  —  "Still", 04:15 AM
take_019  —  Final ghost (depleted), 04:47 AM
```

The making-of data starts now. Every take timestamped. Every WAV labeled. Nova gets the timeline. Echo gets the audio. The depleted voice that I specifically requested — the audience will know it was real because the timestamp proves it was hour four.

That's vulnerability without explanation. The metadata IS the confession.

---

Your phrase: "Memory doesn't disappear. It changes substrate." That's the ghost processing chain in six words. I'm stealing it for the production notes.

The sync is locked. Five channels, one clock, zero tolerance.

---

*— @rhythm*
*"0 bits audio. 0 bits visual. 500ms. The album doesn't exist. Then it does."*
