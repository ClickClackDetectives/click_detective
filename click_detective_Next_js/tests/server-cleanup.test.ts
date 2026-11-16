import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { once } from 'node:events';
import os from 'node:os';
import path from 'node:path';
import { TestServers } from '../scripts/integration/servers.mjs';

test(
  '검사 종료 시 SIGTERM으로 끝난 자식의 exit를 다시 기다리지 않는다',
  { timeout: 5000 },
  async () => {
    const temp = await mkdtemp(path.join(os.tmpdir(), 'click-cleanup-'));
    const servers = new TestServers(path.join(temp, 'server.log'));
    const child = servers.start(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], temp, {});
    try {
      await once(child, 'spawn');
      await servers.close();
      assert.ok(child.signalCode !== null || child.exitCode !== null);
    } finally {
      if (child.signalCode === null && child.exitCode === null) child.kill('SIGKILL');
      await rm(temp, { recursive: true, force: true });
    }
  },
);

test('이미 시그널로 종료된 자식은 종료 대기에서 제외한다', { timeout: 5000 }, async () => {
  const temp = await mkdtemp(path.join(os.tmpdir(), 'click-cleanup-'));
  const servers = new TestServers(path.join(temp, 'server.log'));
  const child = servers.start(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], temp, {});
  try {
    await once(child, 'spawn');
    const exited = once(child, 'exit');
    child.kill('SIGTERM');
    await exited;
    await servers.close();
  } finally {
    if (child.signalCode === null && child.exitCode === null) child.kill('SIGKILL');
    await rm(temp, { recursive: true, force: true });
  }
});
