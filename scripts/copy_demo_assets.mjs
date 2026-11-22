import { cp, mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const destination = path.join(root, 'frontend/dist/demo')
await mkdir(destination, { recursive: true })
await cp(path.join(root, 'docs/demo'), destination, { recursive: true })
console.log('Copied the demo player, recording and captions into the static site.')
