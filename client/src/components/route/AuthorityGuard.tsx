import { PropsWithChildren } from 'react'
import { Navigate } from 'react-router-dom'
import useAuthority from '@/utils/hooks/useAuthority'

type AuthorityGuardProps = PropsWithChildren<{
    userAuthority?: string[]
    authority?: string[]
}>

const AuthorityGuard = (props: AuthorityGuardProps) => {
    const { userAuthority = [], authority = [], children } = props

    const roleMatched = useAuthority(userAuthority, authority)

    // Debug logging
    if (!roleMatched) {
        console.log('[AuthorityGuard] Access denied:', {
            userAuthority,
            authority,
            roleMatched,
        })
    }

    return <>{roleMatched ? children : <Navigate to="/access-denied" />}</>
}

export default AuthorityGuard
