/** A run-scoped, non-release training choice. No arbitrary provider URL/model override. */
export const TRAINING_MODEL_CHOICES = Object.freeze({
  default: null,
  'deepseek-v4-flash': Object.freeze({ provider: 'deepseek-official', model: 'deepseek-v4-flash' }),
});

export function resolveTrainingModelChoice(choice, hostDefault) {
  if (choice === undefined || choice === 'default') {
    if (!hostDefault || typeof hostDefault.provider !== 'string' || typeof hostDefault.model !== 'string') {
      throw new Error('host default training model unavailable');
    }
    return { provider: hostDefault.provider, model: hostDefault.model, choice: 'default' };
  }
  const known = TRAINING_MODEL_CHOICES[choice];
  if (!known || !Object.hasOwn(TRAINING_MODEL_CHOICES, choice)) throw new Error('unsupported training model choice');
  return { ...known, choice };
}
