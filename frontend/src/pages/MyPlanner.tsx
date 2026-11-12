import { useState, useEffect } from 'react'
import { api, type PlannerProfile, isApiError } from '../lib/api'
import { getOrCreateToken, clearToken } from '../lib/token'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { LoadingState } from '../components/ui/States'
import { AlertTriangle, User, Trash2, Save } from 'lucide-react'

type Step = 'loading' | 'setup' | 'ready' | 'error'

const BRANCHES = ['CSE', 'ECE', 'ME', 'EE', 'IT', 'CE', 'Other']
const YEARS = ['1', '2', '3', '4']
const INTEREST_SUGGESTIONS = ['AI', 'data', 'programming', 'networking', 'IoT', 'robotics', 'SQL', 'hardware', 'statistics']

export function MyPlanner() {
  const [step, setStep] = useState<Step>('loading')
  const [profile, setProfile] = useState<PlannerProfile | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // Form fields
  const [alias, setAlias] = useState('')
  const [branch, setBranch] = useState('')
  const [year, setYear] = useState('')
  const [interestInput, setInterestInput] = useState('')
  const [interests, setInterests] = useState<string[]>([])

  const token = getOrCreateToken()

  useEffect(() => {
    api.planner.get(token)
      .then(p => {
        setProfile(p)
        setAlias(p.alias ?? '')
        setBranch(p.branch ?? '')
        setYear(p.year ?? '')
        setInterests(p.interests)
        setStep('ready')
      })
      .catch(e => {
        if (isApiError(e) && e.status === 404) {
          setStep('setup')
        } else {
          setErrorMsg(e.message)
          setStep('error')
        }
      })
  }, [])

  async function createProfile() {
    setSaving(true)
    try {
      await api.planner.create({ token, alias: alias || null, branch: branch || null, year: year || null, interests, preferred_subject_areas: [], completed_electives: [] })
      const p = await api.planner.get(token)
      setProfile(p)
      setStep('ready')
    } catch (e) {
      setErrorMsg(isApiError(e) ? e.message : 'Failed')
    } finally {
      setSaving(false)
    }
  }

  async function saveProfile() {
    if (!profile) return
    setSaving(true)
    try {
      await api.planner.update(token, { token, alias: alias || null, branch: branch || null, year: year || null, interests, preferred_subject_areas: profile.preferred_subject_areas, completed_electives: profile.completed_electives })
      const p = await api.planner.get(token)
      setProfile(p)
    } catch (e) {
      setErrorMsg(isApiError(e) ? e.message : 'Failed')
    } finally {
      setSaving(false)
    }
  }

  async function deleteProfile() {
    if (!confirm('Delete your planner profile? This cannot be undone.')) return
    await api.planner.delete(token)
    clearToken()
    window.location.reload()
  }

  function addInterest() {
    const v = interestInput.trim().toLowerCase()
    if (v && !interests.includes(v)) setInterests(prev => [...prev, v])
    setInterestInput('')
  }

  if (step === 'loading') return <LoadingState message="Loading your planner…" />

  return (
    <div>
      <PageHeader title="My Planner" description="Your pseudonymous elective assistant" />

      {/* Privacy notice */}
      <div className="mb-5 flex items-start gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
        <p className="text-xs text-amber-200/80">
          Your planner is identified by a randomly generated token stored in your browser.
          <strong className="text-amber-200"> This is not a secure account</strong> — clearing browser storage loses your saved data.
          Do not enter your real student ID or personal details.
        </p>
      </div>

      {step === 'error' && (
        <div className="mb-4 flex gap-2 rounded-lg border border-red-500/20 bg-red-500/5 p-3">
          <AlertTriangle className="h-4 w-4 text-red-400" />
          <p className="text-xs text-red-300">{errorMsg}</p>
        </div>
      )}

      {/* Setup */}
      {step === 'setup' && (
        <Card className="max-w-lg">
          <CardHeader>
            <CardTitle>Create Your Profile</CardTitle>
          </CardHeader>
          <p className="mb-4 text-xs text-[#8892a4]">Use an alias only — no real name required.</p>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs text-[#8892a4]">Alias (optional)</label>
              <input
                value={alias}
                onChange={e => setAlias(e.target.value)}
                placeholder="e.g. Student A"
                maxLength={40}
                className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] placeholder-[#8892a4] outline-none focus:border-[#8b5cf6]"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs text-[#8892a4]">Branch</label>
                <select value={branch} onChange={e => setBranch(e.target.value)}
                  className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]">
                  <option value="">Select…</option>
                  {BRANCHES.map(b => <option key={b}>{b}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs text-[#8892a4]">Year</label>
                <select value={year} onChange={e => setYear(e.target.value)}
                  className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]">
                  <option value="">Select…</option>
                  {YEARS.map(y => <option key={y}>{y}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="mb-1 block text-xs text-[#8892a4]">Interests</label>
              <div className="flex gap-2">
                <input
                  value={interestInput}
                  onChange={e => setInterestInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addInterest()}
                  placeholder="Type an interest…"
                  className="flex-1 rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] placeholder-[#8892a4] outline-none focus:border-[#8b5cf6]"
                />
                <Button size="sm" variant="secondary" onClick={addInterest}>Add</Button>
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {INTEREST_SUGGESTIONS.filter(s => !interests.includes(s)).map(s => (
                  <button key={s} onClick={() => setInterests(prev => [...prev, s])}
                    className="rounded-full border border-[#2d3748] px-2 py-0.5 text-xs text-[#8892a4] hover:border-[#8b5cf6]/50 hover:text-[#e2e8f0]">
                    + {s}
                  </button>
                ))}
              </div>
              {interests.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {interests.map(i => (
                    <button key={i} onClick={() => setInterests(p => p.filter(x => x !== i))}
                      className="flex items-center gap-1 rounded-full border border-[#8b5cf6]/30 bg-[#8b5cf6]/10 px-2 py-0.5 text-xs text-[#a78bfa] hover:text-red-400">
                      {i} ×
                    </button>
                  ))}
                </div>
              )}
            </div>
            <Button onClick={createProfile} disabled={saving} className="w-full justify-center">
              <User className="h-4 w-4" />
              {saving ? 'Creating…' : 'Create Profile'}
            </Button>
          </div>
        </Card>
      )}

      {/* Ready */}
      {step === 'ready' && profile && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <div className="flex gap-2">
                <Button size="sm" onClick={saveProfile} disabled={saving}>
                  <Save className="h-3 w-3" />{saving ? 'Saving…' : 'Save'}
                </Button>
                <Button size="sm" variant="danger" onClick={deleteProfile}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </CardHeader>
            <div className="space-y-3">
              <div>
                <label className="mb-1 block text-xs text-[#8892a4]">Alias</label>
                <input value={alias} onChange={e => setAlias(e.target.value)} maxLength={40}
                  className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs text-[#8892a4]">Branch</label>
                  <select value={branch} onChange={e => setBranch(e.target.value)}
                    className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]">
                    <option value="">—</option>
                    {BRANCHES.map(b => <option key={b}>{b}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs text-[#8892a4]">Year</label>
                  <select value={year} onChange={e => setYear(e.target.value)}
                    className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]">
                    <option value="">—</option>
                    {YEARS.map(y => <option key={y}>{y}</option>)}
                  </select>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <CardHeader><CardTitle>Shortlisted Electives</CardTitle></CardHeader>
            {profile.shortlisted_electives.length === 0 ? (
              <p className="text-xs text-[#8892a4]">None shortlisted. Use the Elective Finder to add electives.</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {profile.shortlisted_electives.map(id => (
                  <Badge key={id} variant="purple">{id}</Badge>
                ))}
              </div>
            )}
          </Card>

          <Card>
            <CardHeader><CardTitle>Interests</CardTitle></CardHeader>
            <div className="flex flex-wrap gap-1.5">
              {profile.interests.length === 0
                ? <p className="text-xs text-[#8892a4]">No interests saved.</p>
                : profile.interests.map(i => <Badge key={i} variant="indigo">{i}</Badge>)}
            </div>
          </Card>

          <Card>
            <CardHeader><CardTitle>Saved Comparisons</CardTitle></CardHeader>
            {profile.saved_comparisons.length === 0 ? (
              <p className="text-xs text-[#8892a4]">No comparisons saved yet.</p>
            ) : (
              <ul className="space-y-2 text-xs">
                {profile.saved_comparisons.map((cmp, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="text-[#8892a4]">#{i + 1}</span>
                    {cmp.map(id => <Badge key={id} variant="cyan">{id}</Badge>)}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </div>
  )
}

