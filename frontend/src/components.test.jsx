import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ScoreRing, ToastProvider } from './components/ui'
import { UploadModal } from './pages/Resumes'
import { errorMessage } from './api'
import { Roadmap, MatchReport } from './pages/Matching'

describe('resume upload validation', () => {
  function modal() {
    return render(
      <MemoryRouter>
        <ToastProvider>
          <UploadModal onClose={() => {}} onUploaded={() => {}} />
        </ToastProvider>
      </MemoryRouter>,
    )
  }
  it('rejects an unsupported file before calling the API', () => {
    modal()
    fireEvent.change(screen.getByLabelText('Choose resume file'), {
      target: { files: [new File(['bad'], 'resume.exe')] },
    })
    expect(screen.getByRole('alert')).toHaveTextContent('Choose a PDF or DOCX')
  })
  it('rejects files above 5 MiB', () => {
    modal()
    fireEvent.change(screen.getByLabelText('Choose resume file'), {
      target: {
        files: [new File([new Uint8Array(5 * 1024 * 1024 + 1)], 'big.pdf')],
      },
    })
    expect(screen.getByRole('alert')).toHaveTextContent('5 MiB or smaller')
  })
  it('requires a file and shows a useful error', () => {
    modal()
    fireEvent.click(screen.getByRole('button', { name: 'Upload & analyze' }))
    expect(screen.getByRole('alert')).toHaveTextContent('Choose a resume')
  })
  it('accepts a supported file and fills its title', () => {
    modal()
    fireEvent.change(screen.getByLabelText('Choose resume file'), {
      target: { files: [new File(['pdf'], 'my-career.pdf')] },
    })
    expect(screen.getByLabelText('Resume title')).toHaveValue('my-career')
  })
})

describe('transparent reporting', () => {
  it('exposes an accessible score without converting it to hiring probability', () => {
    render(<ScoreRing score={72.5} label="Documented job alignment" />)
    expect(screen.getByRole('img')).toHaveAccessibleName(
      'Documented job alignment: 72.5 out of 100',
    )
  })
  it('renders learning resources and concrete milestones', () => {
    render(
      <Roadmap
        steps={[
          {
            skill_id: 1,
            name: 'Docker',
            category: 'tool',
            importance: 'essential',
            action: 'Build a container.',
            milestone: 'Deploy a small service.',
            resources: [{ title: 'Docker guide', url: 'https://docs.docker.com/' }],
          },
        ]}
      />,
    )
    expect(screen.getByText('Deploy a small service.')).toBeVisible()
    expect(screen.getByRole('link', { name: 'Docker guide' })).toHaveAttribute('rel', 'noreferrer')
  })
  it('renders empty gaps honestly', () => {
    render(<Roadmap steps={[]} />)
    expect(screen.getByText(/All requested catalog skills/)).toBeVisible()
  })
  it('preserves field errors returned by the backend', () => {
    expect(
      errorMessage({
        response: {
          data: { error: { fields: { file: ['Scanned PDFs need OCR.'] } } },
        },
      }),
    ).toContain('Scanned PDFs need OCR.')
  })
})
