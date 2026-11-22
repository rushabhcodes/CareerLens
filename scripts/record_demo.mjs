/** Record real browser interactions; credentials, raw videos and logs stay ignored. */
import fs from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const require = createRequire(path.join(root, 'frontend/package.json'))
const { chromium, expect } = require('@playwright/test')
const base = process.env.DEMO_BASE_URL || 'https://careerlens.rushabh.dev'
const speed = Number(process.env.DEMO_SPEED || 1)
const directory = path.resolve(root, process.env.DEMO_RECORDING_DIR || '.runtime/demo-recording')
await fs.mkdir(directory, { recursive: true })
const browser = await chromium.launch({
  headless: true,
  ...(process.env.PLAYWRIGHT_EXECUTABLE
    ? { executablePath: process.env.PLAYWRIGHT_EXECUTABLE }
    : {}),
})
const segments = []
const errors = []

async function segment(name, viewport, setup) {
  const context = await browser.newContext({
    baseURL: base,
    viewport,
    recordVideo: { dir: directory, size: viewport },
    reducedMotion: 'reduce',
  })
  if (setup) await setup(context)
  const page = await context.newPage()
  page.setDefaultTimeout(90000)
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('response', (response) => {
    if (response.url().startsWith(base) && response.status() >= 500)
      errors.push(`${response.status()} ${new URL(response.url()).pathname}`)
  })
  const started = Date.now()
  const markers = []
  const clock = () => (Date.now() - started) / 1000
  async function chapter(title, caption, seconds = 5) {
    markers.push({ start: clock(), title, caption })
    console.log(`${name}: ${title}`)
    await page.waitForTimeout(seconds * 1000 * speed)
  }
  async function click(locator) {
    await locator.click()
  }
  async function nav(label) {
    await click(page.getByRole('link', { name: label, exact: true }))
    await page.getByText('Loading your records…', { exact: true }).waitFor({ state: 'hidden' })
    await page.evaluate(() => window.scrollTo(0, 0))
  }
  async function scroll(y) {
    await page.evaluate((value) => window.scrollTo({ top: value, behavior: 'smooth' }), y)
    await page.waitForTimeout(900 * speed)
  }
  async function finish() {
    const duration = clock()
    await context.close()
    const video = await page.video().path()
    segments.push({ name, video, markers, duration, viewport })
  }
  return { page, context, chapter, click, nav, scroll, finish }
}

try {
  const desktop = await segment('Workspace', { width: 1440, height: 1000 })
  const { page, chapter, click, nav, scroll } = desktop
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Welcome to CareerLens.' })).toBeVisible()
  await chapter(
    'CareerLens',
    'A real walkthrough at careerlens.rushabh.dev · fictional candidate data',
    6,
  )
  await click(page.getByRole('button', { name: 'Create account', exact: true }))
  await chapter('Accounts', 'Create your own workspace or explore instantly with sample data.', 4)
  await click(page.getByRole('button', { name: 'Sign in', exact: true }))
  await click(page.getByRole('button', { name: 'Explore sample workspace' }))
  await expect(page.getByRole('heading', { name: 'A little clarity, Alex.' })).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Where your skills could take you', exact: true }),
  ).toBeVisible()
  await chapter(
    'Dashboard',
    'Resume scores, job comparisons, skill gaps and career directions in one view.',
    7,
  )
  await scroll(500)
  await chapter('Progress at a glance', 'Review recent analyses and recommended next steps.', 4)

  await nav('My resumes')
  await chapter('Resume library', 'Organize versions and download private originals.', 4)
  const original = page.waitForEvent('download')
  await click(page.getByRole('button', { name: 'Download Full-stack resume', exact: true }))
  await (await original).saveAs(path.join(directory, 'downloaded-original.pdf'))
  await click(page.getByRole('button', { name: 'Upload resume', exact: true }))
  await page
    .getByLabel('Choose resume file')
    .setInputFiles(path.join(root, 'docs/sample-resume.pdf'))
  await page.getByLabel('Resume title').fill('Recorded PDF resume')
  await chapter(
    'PDF upload',
    'Upload a selectable-text PDF or DOCX. The hosted demo accepts files up to 4 MiB.',
    5,
  )
  await click(page.getByRole('button', { name: 'Upload & analyze' }))
  await expect(
    page.getByRole('heading', { name: 'Recorded PDF resume', exact: true }),
  ).toBeVisible()
  await click(page.getByRole('link', { name: 'View analysis', exact: true }).first())
  await expect(page.getByRole('heading', { name: 'Every point, explained' })).toBeVisible()
  await chapter(
    'Resume analysis',
    'Candidate details, section checks and a quality score with every point explained.',
    8,
  )
  const report = page.waitForEvent('download')
  await click(page.getByRole('button', { name: 'Download report', exact: true }))
  await (await report).saveAs(path.join(directory, 'downloaded-report.json'))
  await scroll(650)
  await chapter(
    'Actionable feedback',
    'See score components and practical suggestions before revising your resume.',
    6,
  )
  await page.getByRole('heading', { name: 'Your skills, with evidence' }).scrollIntoViewIfNeeded()
  await click(page.locator('.evidence-grid summary').first())
  await chapter(
    'Skill evidence',
    'Open a detected skill to inspect the exact supporting resume text.',
    6,
  )

  await nav('My resumes')
  await click(page.getByRole('button', { name: 'Upload resume', exact: true }))
  await page
    .getByLabel('Choose resume file')
    .setInputFiles(path.join(root, 'docs/sample-resume.docx'))
  await page.getByLabel('Resume title').fill('Recorded DOCX resume')
  await click(page.getByRole('button', { name: 'Upload & analyze' }))
  await expect(
    page.getByRole('heading', { name: 'Recorded DOCX resume', exact: true }),
  ).toBeVisible()
  await chapter(
    'DOCX support',
    'Word resumes use the same extraction, skill matching and scoring pipeline.',
    5,
  )

  await nav('Job descriptions')
  await click(page.getByRole('button', { name: 'Add job description', exact: true }))
  await page.getByLabel('Job title', { exact: true }).fill('Demo Python developer')
  await page.getByLabel('Company', { exact: true }).fill('Fictional Studio')
  await page
    .getByLabel('Job description', { exact: true })
    .fill(
      'Build Python and Django REST APIs with SQL. Deploy with Docker and AWS. Use automated Testing and Git in a collaborative team.',
    )
  await page.getByLabel('Required experience (years)').fill('2')
  await page.getByLabel('Qualification phrase').fill('MCA')
  await chapter(
    'Job descriptions',
    'Save a target role, experience and qualifications. Skills can be detected from its text.',
    6,
  )
  await click(page.getByRole('button', { name: 'Save job description', exact: true }))
  await expect(
    page.getByRole('heading', { name: 'Demo Python developer', exact: true }),
  ).toBeVisible()
  await click(page.getByRole('button', { name: 'Edit Demo Python developer', exact: true }))
  await page.getByLabel('Company', { exact: true }).fill('Fictional Studio · updated')
  await chapter(
    'Editable requirements',
    'Review detected skills and set essential or preferred importance.',
    5,
  )
  await click(page.getByRole('button', { name: 'Save changes', exact: true }))
  await expect(
    page.getByRole('heading', { name: 'Demo Python developer', exact: true }),
  ).toBeVisible()
  await click(page.getByRole('link', { name: 'Check my match', exact: true }).first())
  await click(page.getByRole('button', { name: 'Analyze match', exact: true }))
  await expect(page.getByRole('heading', { name: 'The reasoning behind your score' })).toBeVisible()
  await chapter(
    'Job matching',
    'Compare skills, explicit experience and qualifications. Scores measure documented alignment.',
    7,
  )
  await scroll(450)
  await chapter(
    'Matched, related and missing',
    'Related skills earn partial credit. Missing requirements remain visible.',
    6,
  )
  await scroll(900)
  await chapter(
    'Transparent scoring',
    'Review the weighted calculation and the evidence behind each component.',
    5,
  )

  await nav('Skill gap analysis')
  await expect(page.getByRole('heading', { name: 'Your learning roadmap' })).toBeVisible()
  await chapter(
    'Skill gap roadmap',
    'Turn missing skills into prioritized actions, milestones and learning resources.',
    7,
  )
  await scroll(650)
  await page.waitForTimeout(3000 * speed)

  await nav('Career pathways')
  await click(page.getByLabel('Include optional AI learning advice'))
  await click(page.getByRole('button', { name: 'Explore pathways', exact: true }))
  await expect(
    page.getByRole('heading', { name: 'Full-stack developer', exact: true }),
  ).toBeVisible()
  await chapter(
    'Career recommendations',
    'Explore roles ranked by explicit skill coverage. Provider enrichment is optional.',
    7,
  )
  await click(page.getByRole('button', { name: 'View learning plan', exact: true }).first())
  await expect(page.getByRole('heading', { name: 'Your learning plan', exact: true })).toBeVisible()
  await page
    .getByRole('heading', { name: 'Your learning plan', exact: true })
    .scrollIntoViewIfNeeded()
  await chapter(
    'Personal learning plans',
    'Without provider credentials, CareerLens keeps the labeled rule-based result.',
    7,
  )

  await nav('Analysis history')
  await expect(page.getByRole('heading', { name: 'Every step, in perspective.' })).toBeVisible()
  await chapter(
    'Analysis history',
    'Reopen saved resume reviews, job matches and career recommendations.',
    6,
  )
  await page.getByLabel('Search analysis history').fill('Recorded')
  await page.waitForTimeout(1000)
  await chapter(
    'Search saved work',
    'Filter previous analyses without losing the underlying reports.',
    4,
  )

  await nav('My profile')
  await page
    .getByLabel('Your next career goal')
    .fill('Build and demonstrate a full-stack Python portfolio.')
  await click(page.getByRole('button', { name: 'Save profile', exact: true }))
  await chapter(
    'Profile and persistence',
    'Save your career goal. Account-owned data persists beyond the current page.',
    5,
  )
  await page.reload()
  await expect(page.getByLabel('Your next career goal')).toHaveValue(
    'Build and demonstrate a full-stack Python portfolio.',
  )
  await click(page.getByRole('link', { name: 'How scoring works', exact: false }))
  await expect(page.getByRole('heading', { name: 'A score you can understand.' })).toBeVisible()
  await chapter(
    'How scoring works',
    'Read the formulas, parsing limits, privacy controls and optional AI behavior.',
    6,
  )
  await scroll(650)
  await page.waitForTimeout(3000 * speed)

  await nav('My resumes')
  await click(page.getByRole('button', { name: 'Delete Recorded DOCX resume', exact: true }))
  await chapter(
    'Control your files',
    'Deletion removes the original document and its dependent analyses.',
    4,
  )
  await click(page.getByRole('button', { name: 'Delete resume', exact: true }))
  await expect(
    page.getByRole('heading', { name: 'Recorded DOCX resume', exact: true }),
  ).toHaveCount(0)
  await nav('Overview')
  await expect(page.getByRole('heading', { name: 'A little clarity, Alex.' })).toBeVisible()
  await chapter(
    'Your next chapter',
    'Try it yourself: careerlens.rushabh.dev · Explore sample workspace',
    6,
  )
  const sampleToken = await page.evaluate(() => sessionStorage.getItem('careerlens-token'))
  await desktop.finish()

  const staffPath = process.env.DEMO_STAFF_SESSION
  if (staffPath) {
    const staff = JSON.parse(await fs.readFile(path.resolve(root, staffPath), 'utf8'))
    const admin = await segment(
      'Administration',
      { width: 1440, height: 1000 },
      async (context) => {
        await context.addInitScript(
          (token) => sessionStorage.setItem('careerlens-token', token),
          staff.token,
        )
        await context.addCookies([
          {
            name: 'sessionid',
            value: staff.sessionid,
            url: base,
            httpOnly: true,
            secure: base.startsWith('https:'),
            sameSite: 'Lax',
          },
        ])
      },
    )
    await admin.page.goto('/admin')
    await expect(
      admin.page.getByRole('heading', { name: 'System activity', exact: true }),
    ).toBeVisible()
    await admin.chapter(
      'Staff administration',
      'Authorized staff can inspect application statistics. Visitors cannot access this module.',
      7,
    )
    await admin.page.goto('/django-admin/')
    await expect(
      admin.page.getByRole('heading', { name: 'Site administration', exact: true }),
    ).toBeVisible()
    await admin.chapter(
      'Django administration',
      'Manage the shared catalog through the permission-protected staff interface.',
      5,
    )
    await admin.click(admin.page.getByRole('link', { name: 'Skills', exact: true }))
    await expect(
      admin.page.getByRole('heading', { name: 'Select skill to change', exact: true }),
    ).toBeVisible()
    await admin.chapter(
      'Managed skill catalog',
      'Maintain skills, aliases, related-skill relationships, roles and learning resources.',
      7,
    )
    await admin.finish()
  }

  const mobile = await segment('Mobile', { width: 390, height: 844 }, async (context) => {
    await context.addInitScript(
      (token) => sessionStorage.setItem('careerlens-token', token),
      sampleToken,
    )
  })
  await mobile.page.goto('/')
  await expect(mobile.page.getByRole('heading', { name: 'A little clarity, Alex.' })).toBeVisible()
  await mobile.chapter('Mobile workspace', 'The dashboard adapts to a phone-sized screen.', 6)
  await mobile.click(mobile.page.getByRole('button', { name: 'Open navigation', exact: true }))
  await mobile.chapter('Mobile navigation', 'Open the menu to reach every workspace module.', 4)
  await mobile.click(mobile.page.getByRole('link', { name: 'Skill gap analysis', exact: true }))
  await expect(mobile.page.getByRole('heading', { name: 'Your learning roadmap' })).toBeVisible()
  await mobile.chapter(
    'Learning on the go',
    'Review skill gaps and practical next steps on mobile.',
    6,
  )
  if (!(await mobile.page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)))
    throw new Error('Mobile page overflows the viewport.')
  await mobile.finish()
  if (errors.length) throw new Error(errors.join('\n'))
  await fs.writeFile(
    path.join(directory, 'recording.json'),
    JSON.stringify({ base, segments, errors }, null, 2),
  )
  console.log('Saved recording metadata:', path.join(directory, 'recording.json'))
} finally {
  await browser.close()
}
