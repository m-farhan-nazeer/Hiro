import axios from 'axios'
import type {
    SignInCredential,
    SignUpCredential,
    ForgotPassword,
    ResetPassword,
    SignInResponse,
    SignUpResponse,
} from '@/@types/auth'

// Django backend base URL (dev)
const AUTH_BASE_URL = 'http://localhost:8000'

const authClient = axios.create({
    baseURL: AUTH_BASE_URL,
    withCredentials: true,
    timeout: 30000, // 30 second timeout
    headers: {
        'Content-Type': 'application/json',
    },
})

export async function apiSignIn(data: SignInCredential) {
    const payload = {
        username: data.userName,
        password: data.password,
    }

    return authClient.post<SignInResponse>('/users/login/', payload)
}

export async function apiSignUp(data: SignUpCredential) {
    const payload = {
        username: data.userName,
        email: data.email,
        password: data.password,
        password_confirm: data.password,
    }

    console.log('[AuthService] apiSignUp calling:', '/users/register/', payload)
    try {
        const response = await authClient.post<SignUpResponse>('/users/register/', payload)
        console.log('[AuthService] apiSignUp response received:', response.status, response.data)
        return response
    } catch (error) {
        console.error('[AuthService] apiSignUp error:', error)
        throw error
    }
}

export async function apiGetCurrentUser() {
    return authClient.get<SignInResponse>('/users/me/')
}

export async function apiSignOut() {
    return authClient.post('/users/logout/')
}

export async function apiForgotPassword(data: ForgotPassword) {
    // Still uses mock / placeholder behaviour for now
    return authClient.post('/forgot-password', data)
}

export async function apiResetPassword(data: ResetPassword) {
    // Still uses mock / placeholder behaviour for now
    return authClient.post('/reset-password', data)
}
