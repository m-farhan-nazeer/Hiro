import Side from './Side'
// import Cover from './Cover'
// import Simple from './Simple'
import View from '@/views'
import { useAppSelector } from '@/store'
import { LAYOUT_TYPE_BLANK } from '@/constants/theme.constant'
import { useLocation } from 'react-router-dom'

const AuthLayout = () => {
    const layoutType = useAppSelector((state) => state.theme.layout.type)
    const location = useLocation()

    // Skip Side layout for public application form route
    const isPublicApplicationRoute = location.pathname === '/apply'

    return (
        <div className="app-layout-blank flex flex-auto flex-col h-[100vh]">
            {layoutType === LAYOUT_TYPE_BLANK || isPublicApplicationRoute ? (
                <View />
            ) : (
                <Side>
                    <View />
                </Side>
            )}
        </div>
    )
}

export default AuthLayout

