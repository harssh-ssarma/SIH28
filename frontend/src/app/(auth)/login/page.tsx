'use client'

import { useState, useRef } from 'react'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema, type LoginFormData } from '@/lib/validations'
import { CardProgress, type CardProgressHandle } from '@/components/ui/CardProgress'
import { OutlinedInput } from '@/components/ui/OutlinedInput'
import { EyeOpen, EyeOff } from '@/components/ui/PasswordToggleIcons'



export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [loginError, setLoginError] = useState<string | null>(null)
  const { login, user } = useAuth()
  const router = useRouter()
  const cardProgressRef = useRef<CardProgressHandle>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onChange',
  })

  const ROLE_DASHBOARD: Record<string, string> = {
    admin:     '/admin/dashboard',
    org_admin: '/admin/dashboard',
    faculty:   '/faculty/dashboard',
    student:   '/student/dashboard',
  }

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setLoginError(null)
    cardProgressRef.current?.start()
    try {
      await login(data.username, data.password)
      cardProgressRef.current?.finish()
      const raw = localStorage.getItem('user')
      const role = raw ? (JSON.parse(raw).role?.toLowerCase() ?? '') : ''
      router.push(ROLE_DASHBOARD[role] ?? '/admin/dashboard')
    } catch (err) {
      cardProgressRef.current?.reset()
      const status = (err as any)?.status ?? 0
      const msg    = err instanceof Error ? err.message : ''

      if (status === 0 || msg === 'Failed to fetch' || msg.toLowerCase().includes('networkerror')) {
        // fetch() threw — server is not reachable at all
        setLoginError('Cannot connect to the server. Please make sure the backend is running.')
      } else if (status >= 500) {
        setLoginError('Server error. Please try again in a moment.')
      } else if (status === 403) {
        setLoginError('Your account has been disabled. Contact your administrator.')
      } else {
        // 401 or any other auth failure — wrong credentials
        setLoginError('Wrong username or password. Try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  // If user is authenticated (set synchronously from localStorage or after
  // background verification), redirect immediately — no blank screen, no flash.
  if (user) {
    const role = user.role?.toLowerCase() ?? ''
    const ROLE_DASHBOARD: Record<string, string> = {
      admin:     '/admin/dashboard',
      org_admin: '/admin/dashboard',
      faculty:   '/faculty/dashboard',
      student:   '/student/dashboard',
    }
    router.replace(ROLE_DASHBOARD[role] ?? '/admin/dashboard')
    return null
  }

  return (
    <>
      {/* ── Page shell — uses --color-bg-page token so light/dark are consistent ── */}
      <div
        className="min-h-screen flex flex-col items-center justify-center px-4 py-10"
        style={{ background: 'var(--color-bg-page)' }}
      >

        {/* ── Card — M3 extra-large shape, surface bg, hairline border, modal elevation ── */}
        <div
          className="relative w-full max-w-[450px] px-10 py-10 sm:px-12 overflow-hidden"
          style={{
            background:    'var(--color-bg-surface)',
            border:        '1px solid var(--color-border)',
            borderRadius:  'var(--radius-extra-large)',
            boxShadow:     'var(--shadow-modal)',
          }}
        >

          {/* ── In-card progress bar (Google-style, top of card) ── */}
          <CardProgress ref={cardProgressRef} />

          {/* ── Header ── */}
          <div className="flex flex-col items-center gap-2 mb-8">
            <Image
              src="/logo2.png"
              alt="Cadence"
              width={72}
              height={72}
              priority
              quality={100}
              className="rounded-full object-contain mix-blend-multiply dark:mix-blend-screen"
            />
            <h1
              className="text-[24px] font-normal mt-1"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Sign in
            </h1>
            <p
              className="text-[14px]"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              to continue to Cadence
            </p>
          </div>

          {/* ── Form ── */}
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

            {/* Dim + block interaction while loading */}
            <div
              className="flex flex-col gap-5"
              style={{
                opacity:       isLoading ? 0.45 : 1,
                pointerEvents: isLoading ? 'none' : 'auto',
                transition:    'opacity 150ms ease',
              }}
            >

            <OutlinedInput
              id="username"
              label="Username or email"
              type="text"
              autoComplete="username"
              placeholder=""
              disabled={isLoading}
              error={errors.username?.message}
              {...register('username')}
            />

            <OutlinedInput
              id="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder=""
              disabled={isLoading}
              error={errors.password?.message}
              suffix={
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  disabled={isLoading}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="p-1 rounded-full transition-colors disabled:pointer-events-none"
                  style={{ color: 'var(--color-text-secondary)' }}
                  onMouseEnter={e => ((e.currentTarget as HTMLElement).style.background = 'var(--color-bg-surface-2)')}
                  onMouseLeave={e => ((e.currentTarget as HTMLElement).style.background = 'transparent')}
                >
                  {showPassword ? <EyeOff /> : <EyeOpen />}
                </button>
              }
              {...register('password')}
            />

            </div>

            {/* Forgot password — M3: right-aligned text button */}
            <div className="flex justify-end -mt-2">
              <a
                href="#"
                className="text-[14px] hover:underline transition-colors"
                style={{ color: 'var(--color-text-link)' }}
              >
                Forgot password?
              </a>
            </div>

            {/* ── Inline error — M3 error color tokens ── */}
            {loginError && (
              <p
                className="text-[13px] flex items-center gap-1.5 -mt-1"
                style={{ color: 'var(--color-danger)' }}
              >
                <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {loginError}
              </p>
            )}

            {/* ── Bottom row: Create account (left) + Sign in (right) ── */}
            <div className="flex items-center justify-between mt-1">
              <a
                href="#"
                className="text-[14px] hover:underline transition-colors"
                style={{ color: 'var(--color-text-link)' }}
              >
                Create account
              </a>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary disabled:opacity-60 disabled:cursor-not-allowed"
              >
                Sign in
              </button>
            </div>

          </form>
        </div>

        {/* ── Footer ── */}
        <p
          className="text-[12px] mt-8"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          &copy; {new Date().getFullYear()} Cadence Platform
        </p>
      </div>
    </>
  )
}
