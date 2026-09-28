import path from 'node:path';
const registryKey = Symbol.for('dsh.ptc.trainer.services.v1');
const services = globalThis[registryKey] ||= new Map();
export function registerTrainerRuntime(root, service) {
  const key=path.resolve(root); services.set(key,service);
  return () => { if (services.get(key) === service) services.delete(key); };
}
export function getTrainerRuntime(root) {
  const service=services.get(path.resolve(root));
  if (!service) throw new Error('Agent Trainer control service is not loaded');
  return service;
}
