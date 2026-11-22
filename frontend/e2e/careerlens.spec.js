import { test, expect } from '@playwright/test'
import path from 'node:path'

const email = `browser-${Date.now()}@example.com`
const password = 'BrowserTest!CareerLens42'

test('a complete real-account workflow persists resumes, jobs, matches and profile', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/login')
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await page.getByLabel('First name').fill('Taylor')
  await page.getByLabel('Last name').fill('River')
  await page.getByLabel('Email address').fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Create my workspace' }).click()
  await expect(page.getByRole('heading', { name: 'A little clarity, Taylor.' })).toBeVisible()
  await expect(page.getByText('Your progress starts here')).toBeVisible()

  await page.getByRole('link', { name: 'Upload resume', exact: true }).first().click()
  await page
    .getByLabel('Choose resume file')
    .setInputFiles(path.resolve('../docs/sample-resume.pdf'))
  await page.getByLabel('Resume title').fill('Browser integration resume')
  await page.getByRole('button', { name: 'Upload & analyze' }).click()
  await expect(page.getByRole('heading', { name: 'Browser integration resume' })).toBeVisible()
  await page.getByRole('link', { name: 'View analysis' }).click()
  await expect(page.getByRole('heading', { name: 'Every point, explained' })).toBeVisible()
  await expect(page.getByText('alex.morgan@example.com', { exact: true })).toBeVisible()
  const reportDownload = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download report' }).click()
  expect((await reportDownload).suggestedFilename()).toBe('careerlens-resume-report.json')

  await page.getByRole('link', { name: 'Job descriptions', exact: true }).click()
  await page.getByRole('button', { name: 'Add job description' }).click()
  await page.getByLabel('Job title', { exact: true }).fill('Integration backend role')
  await page.getByLabel('Company', { exact: true }).fill('Test-only company')
  await page
    .getByLabel('Job description', { exact: true })
    .fill(
      'Build reliable Python and Django services with Docker deployments and automated testing.',
    )
  await page.getByLabel('Required experience (years)').fill('2')
  await page.getByLabel('Qualification phrase').fill('MCA')
  await page.getByRole('button', { name: 'Save job description' }).click()
  await expect(page.getByRole('heading', { name: 'Integration backend role' })).toBeVisible()
  await page.getByRole('button', { name: 'Edit Integration backend role' }).click()
  await page.getByLabel('Company', { exact: true }).fill('Edited test company')
  await page.getByRole('button', { name: 'Save changes' }).click()
  await expect(page.getByText('Edited test company', { exact: true })).toBeVisible()
  await page.getByRole('link', { name: 'Check my match' }).click()
  await page.getByRole('button', { name: 'Analyze match' }).click()
  await expect(page.getByRole('heading', { name: 'The reasoning behind your score' })).toBeVisible()
  await expect(page.getByText(/not a probability of getting hired/)).toBeVisible()
  await page.getByRole('link', { name: 'Skill gap analysis', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your learning roadmap' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Docker', exact: true })).toBeVisible()

  await page.getByRole('link', { name: 'Career pathways', exact: true }).click()
  await page.getByRole('button', { name: 'Explore pathways', exact: true }).click()
  await expect(
    page.getByRole('heading', { name: 'Full-stack developer', exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'View learning plan' }).first().click()
  await expect(page.getByRole('heading', { name: 'Your learning plan' })).toBeVisible()
  await page.getByRole('link', { name: 'Analysis history', exact: true }).click()
  await expect(page.getByText(/Resume review · Browser integration resume/)).toBeVisible()
  await page.getByRole('link', { name: 'My profile', exact: true }).click()
  await page
    .getByLabel('Your next career goal')
    .fill('Build and demonstrate a Django portfolio project.')
  await page.getByRole('button', { name: 'Save profile' }).click()
  await page.reload()
  await expect(page.getByLabel('Your next career goal')).toHaveValue(
    'Build and demonstrate a Django portfolio project.',
  )
  await page.getByRole('button', { name: 'Sign out', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Welcome to CareerLens.' })).toBeVisible()
  await page.getByLabel('Email address').fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Sign in to your workspace' }).click()
  await expect(page.getByRole('heading', { name: 'A little clarity, Taylor.' })).toBeVisible()
  await page.getByRole('link', { name: 'My resumes', exact: true }).click()
  await page.getByRole('button', { name: 'Delete Browser integration resume' }).click()
  await page.getByRole('button', { name: 'Delete resume', exact: true }).click()
  await expect(
    page.getByRole('heading', {
      name: 'A fresh perspective starts with your resume',
    }),
  ).toBeVisible()
  expect(errors).toEqual([])
})

test('sample workspace renders all modules and desktop screenshots without browser errors', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/login')
  await page.screenshot({
    path: '../docs/screenshots/01-sign-in.png',
    fullPage: true,
  })
  await page.getByRole('button', { name: 'Explore sample workspace' }).click()
  await expect(page.getByRole('heading', { name: 'A little clarity, Alex.' })).toBeVisible()
  await expect(page.getByText('Sample workspace', { exact: true }).first()).toBeVisible()
  await expect(
    page.getByRole('heading', {
      name: 'Where your skills could take you',
      exact: true,
    }),
  ).toBeVisible()
  await page.screenshot({
    path: '../docs/screenshots/02-dashboard.png',
    fullPage: true,
  })
  for (const [name, heading, file] of [
    ['My resumes', 'My resumes', '03-resumes'],
    ['Resume analysis', 'Every point, explained', '04-resume-analysis'],
    ['Job descriptions', 'Job descriptions', '05-job-descriptions'],
    ['Job match', 'Saved comparisons', '06-job-match'],
    ['Skill gap analysis', 'Your learning roadmap', '07-skill-gaps'],
    ['Career pathways', 'Full-stack developer', '08-career-pathways'],
    ['Analysis history', 'Every step, in perspective.', '09-history'],
    ['My profile', 'Personal details', '10-profile'],
  ]) {
    await page.getByRole('link', { name, exact: true }).click()
    await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible()
    if (name === 'Job match') {
      await page.getByRole('button', { name: /Frontend developer.*Full-stack resume/ }).click()
      await expect(
        page.getByRole('heading', { name: 'The reasoning behind your score' }),
      ).toBeVisible()
    }
    await expect(page.getByText('Loading your records…', { exact: true })).toHaveCount(0)
    await page.screenshot({
      path: `../docs/screenshots/${file}.png`,
      fullPage: true,
    })
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)
  }
  expect(errors).toEqual([])
})

test('mobile navigation and reports fit a 390px viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/login')
  await page.getByRole('button', { name: 'Explore sample workspace' }).click()
  await expect(page.getByRole('heading', { name: 'A little clarity, Alex.' })).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Where your skills could take you', exact: true }),
  ).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await page.screenshot({
    path: '../docs/screenshots/11-mobile-dashboard.png',
    fullPage: true,
  })
  await page.getByRole('button', { name: 'Open navigation' }).click()
  await page.getByRole('link', { name: 'Skill gap analysis', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your learning roadmap' })).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await page.screenshot({
    path: '../docs/screenshots/12-mobile-roadmap.png',
    fullPage: true,
  })
})

test('a local staff account can inspect statistics and manage the Django catalog', async ({
  page,
}) => {
  const { existsSync, readFileSync } = await import('node:fs')
  const credentialsPath = path.resolve('../.runtime/admin-credentials.txt')
  test.skip(
    !existsSync(credentialsPath),
    'Create a local administrator with scripts/create_local_admin.py to run this optional staff flow.',
  )
  const text = readFileSync(credentialsPath, 'utf8')
  const email = text.match(/Frontend email: (.+)/)[1]
  const username = text.match(/Django admin username: (.+)/)[1]
  const password = text.match(/Password: (.+)/)[1]
  await page.goto('/login')
  await page.getByLabel('Email address').fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Sign in to your workspace' }).click()
  await page.getByRole('link', { name: 'Administration', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'System activity' })).toBeVisible()
  await page.screenshot({
    path: '../docs/screenshots/13-administration.png',
    fullPage: true,
  })
  await page.goto('/admin/')
  await page.getByLabel('Username:').fill(username)
  await page.getByLabel('Password:').fill(password)
  await page.getByRole('button', { name: 'Log in', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Site administration' })).toBeVisible()
  await page.getByRole('link', { name: 'Skills', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Select skill to change' })).toBeVisible()
  await page.screenshot({
    path: '../docs/screenshots/14-django-admin-skills.png',
    fullPage: true,
  })
})
