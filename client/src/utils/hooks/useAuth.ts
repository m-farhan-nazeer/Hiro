import { useEffect } from 'react'
import { apiSignIn, apiSignOut, apiSignUp, apiGetCurrentUser } from '@/services/AuthService'
import {
    setUser,
    signInSuccess,
    signOutSuccess,
    useAppSelector,
    useAppDispatch,
} from '@/store'
import appConfig from '@/configs/app.config'
import { REDIRECT_URL_KEY } from '@/constants/app.constant'
import { ADMIN, USER } from '@/constants/roles.constant'
import { useNavigate } from 'react-router-dom'
import useQuery from './useQuery'
import type { SignInCredential, SignUpCredential } from '@/@types/auth'

type Status = 'success' | 'failed'

function useAuth() {
    const dispatch = useAppDispatch()

    const navigate = useNavigate()

    const query = useQuery()

    const { signedIn } = useAppSelector((state) => state.auth.session)
    const user = useAppSelector((state) => state.auth.user)

    const resolveAuthority = (role?: string) => {
        if (role === ADMIN || role === 'super_admin') {
            return [ADMIN]
        }
        return [USER]
    }

    // Check for existing session on app load
    useEffect(() => {
        const checkSession = async () => {
            // Only check if we're not already signed in and don't have user data
            if (!signedIn && !user.userName) {
                try {
                    const resp = await apiGetCurrentUser()
                    if (resp.data) {
                        // Valid session exists, restore user state
                        dispatch(signInSuccess())
                        dispatch(
                            setUser({
                                avatar: resp.data.profile?.avatar || '',
                                userName: resp.data.username || 'Anonymous',
                                authority: resolveAuthority(resp.data.profile?.role),
                                email: resp.data.email || '',
                            })
                        )
                    }
                } catch (error: any) {
                    // No valid session, user will need to log in
                    // Silently fail - this is expected if user is not logged in
                    // Only log if it's not a 403 (which means no session)
                    if (error?.response?.status !== 403) {
                        console.warn('[useAuth] Session check failed:', error)
                    }
                }
            }
        }

        checkSession()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []) // Only run once on mount

    const signIn = async (
        values: SignInCredential
    ): Promise<{
        status: Status
        message: string
    }> => {
        // dispatch(signInSuccess('exampleToken'))
        // const redirectUrl = query.get(REDIRECT_URL_KEY)
        // navigate(
        //     // redirectUrl ? redirectUrl : 
        //     appConfig.authenticatedEntryPath)
        // return {
        //     status: 'success',
        //     message: ''
        // }
        try {
            const resp = await apiSignIn(values)
            
            if (!resp.data) {
                return {
                    status: 'failed',
                    message: 'Login succeeded but no user data received.',
                }
            }

            dispatch(signInSuccess())
            dispatch(
                setUser({
                    avatar: resp.data.profile?.avatar || '',
                    userName: resp.data.username || 'Anonymous',
                    authority: resolveAuthority(resp.data.profile?.role),
                    email: resp.data.email || '',
                })
            )
            const redirectUrl = query.get(REDIRECT_URL_KEY)
            navigate(
                redirectUrl ? redirectUrl : appConfig.authenticatedEntryPath
            )
            return {
                status: 'success',
                message: '',
            }
            // eslint-disable-next-line  @typescript-eslint/no-explicit-any
        } catch (errors: any) {
            const data = errors?.response?.data
            let message = ''

            if (typeof data === 'string') {
                message = data
            } else if (data?.detail) {
                message = data.detail
            } else if (data) {
                // Flatten DRF field errors: { field: ["msg1", "msg2"], ... }
                const parts: string[] = []
                Object.entries(data).forEach(([field, value]) => {
                    if (Array.isArray(value)) {
                        parts.push(`${field}: ${value.join(' ')}`)
                    } else {
                        parts.push(`${field}: ${String(value)}`)
                    }
                })
                message = parts.join(' | ')
            }

            return {
                status: 'failed',
                message: message || errors.toString(),
            }
        }
    }

    const signUp = async (values: SignUpCredential): Promise<{
        status: Status
        message: string
    }> => {
        try {
            console.log('[useAuth] Starting registration...', values.userName)
            const resp = await apiSignUp(values)
            console.log('[useAuth] Registration response:', resp.status, resp.data)
            
            if (!resp.data) {
                console.error('[useAuth] No user data in registration response')
                return {
                    status: 'failed',
                    message: 'Registration succeeded but no user data received.',
                }
            }

            // After successful registration, automatically log the user in
            // by calling the login endpoint with the same credentials
            try {
                console.log('[useAuth] Attempting auto-login after registration...')
                const loginResp = await apiSignIn({
                    userName: values.userName,
                    password: values.password,
                })
                console.log('[useAuth] Auto-login response:', loginResp.status, loginResp.data)

                if (loginResp?.data) {
                    console.log('[useAuth] Auto-login successful, dispatching actions...')
                    dispatch(signInSuccess())
                    dispatch(
                        setUser({
                            avatar: loginResp.data.profile?.avatar || '',
                            userName: loginResp.data.username || 'Anonymous',
                            authority: resolveAuthority(loginResp.data.profile?.role),
                            email: loginResp.data.email || '',
                        })
                    )
                    const redirectUrl = query.get(REDIRECT_URL_KEY)
                    const targetPath = redirectUrl ? redirectUrl : appConfig.authenticatedEntryPath
                    console.log('[useAuth] Navigating to:', targetPath)
                    navigate(targetPath)
                    console.log('[useAuth] Navigation called, returning success')
                    return {
                        status: 'success',
                        message: '',
                    }
                } else {
                    console.error('[useAuth] Auto-login succeeded but no user data')
                    // Registration succeeded but auto-login failed
                    return {
                        status: 'failed',
                        message: 'Account created but automatic login failed. Please sign in manually.',
                    }
                }
            } catch (loginError: any) {
                console.error('[useAuth] Auto-login error:', loginError)
                // Registration succeeded but auto-login failed
                const loginErrorData = loginError?.response?.data
                let loginErrorMessage = 'Account created but automatic login failed. Please sign in manually.'
                
                if (loginErrorData?.detail) {
                    loginErrorMessage = `Account created. ${loginErrorData.detail} Please sign in manually.`
                } else if (loginErrorData) {
                    loginErrorMessage = `Account created. Login error: ${JSON.stringify(loginErrorData)}. Please sign in manually.`
                }
                
                return {
                    status: 'failed',
                    message: loginErrorMessage,
                }
            }
            // eslint-disable-next-line  @typescript-eslint/no-explicit-any
        } catch (errors: any) {
            const data = errors?.response?.data
            let message = ''

            if (typeof data === 'string') {
                message = data
            } else if (data?.detail) {
                message = data.detail
            } else if (data) {
                const parts: string[] = []
                Object.entries(data).forEach(([field, value]) => {
                    if (Array.isArray(value)) {
                        parts.push(`${field}: ${value.join(' ')}`)
                    } else {
                        parts.push(`${field}: ${String(value)}`)
                    }
                })
                message = parts.join(' | ')
            }

            return {
                status: 'failed',
                message: message || errors.toString(),
            }
        }
    }

    const handleSignOut = () => {
        dispatch(signOutSuccess())
        dispatch(
            setUser({
                avatar: '',
                userName: '',
                email: '',
                authority: [],
            })
        )
        navigate(appConfig.unAuthenticatedEntryPath)
    }

    const signOut = async () => {
        try {
            await apiSignOut()
        } catch (error: any) {
            // If logout fails (e.g., 403), still clear local state
            console.warn('[useAuth] Logout API call failed, clearing local state anyway:', error)
        }
        handleSignOut()
    }

    return {
        authenticated: signedIn,
        signIn,
        signUp,
        signOut,
    }
}

export default useAuth
