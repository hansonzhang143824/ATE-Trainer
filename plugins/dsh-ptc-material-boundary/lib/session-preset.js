/**
 * Which preset a session actually runs under.
 *
 * Mirrors `@deepseek-ai/dsh-agent-presets`' own `resolveSessionPreset` exactly:
 * the NEWEST `agent-preset/selected` event wins, and the creation header is only
 * the fallback. Reading the header alone is wrong for a session that switched
 * preset while blank — the log is the authority, because the switch outlives the
 * blank window and every later turn runs under the newly mounted composition.
 *
 * The material boundary needs this because the training-session rule keys off the
 * preset: a header-only read would silently fail to confine a session that the
 * user switched INTO a training preset.
 */
export function resolveSessionPreset(session) {
  const events = Array.isArray(session?.events) ? session.events : [];
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    if (event?.type === 'agent-preset/selected') return event.data?.agentPreset;
  }
  return session?.header?.agentPreset;
}

/** The same answer, taken from an agent. */
export function agentPresetOf(agent) {
  return resolveSessionPreset(agent?.session);
}
