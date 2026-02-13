export type SignInCredential = {
    userName: string
    password: string
}

// Backend (Django) auth types
export type BackendUserProfile = {
    role?: string
    name: string
    telephone: string
    avatar: string | null
    department: string
    position: string
    language: string
    timezone: string
    password_last_changed: string | null
}

export type BackendUser = {
    id: number
    username: string
    first_name: string
    last_name: string
    email: string
    profile: BackendUserProfile
}

export type SignInResponse = BackendUser

export type SignUpResponse = BackendUser

export type SignUpCredential = {
    userName: string
    email: string
    password: string
}

export type ForgotPassword = {
    email: string
}

export type ResetPassword = {
    password: string
}
