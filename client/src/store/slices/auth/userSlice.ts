import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { SLICE_BASE_NAME } from './constants'

export type UserState = {
    avatar?: string
    userName?: string
    displayName?: string
    email?: string
    authority?: string[]
    title?: string
}

const initialState: UserState = {
    avatar: '',
    userName: '',
    displayName: '',
    email: '',
    authority: [],
    title: '',
}

const userSlice = createSlice({
    name: `${SLICE_BASE_NAME}/user`,
    initialState,
    reducers: {
        setUser(state, action: PayloadAction<UserState>) {
            state.avatar = action.payload?.avatar
            state.email = action.payload?.email
            state.userName = action.payload?.userName
            state.displayName = action.payload?.displayName
            state.authority = action.payload?.authority
            state.title = action.payload?.title
        },
    },
})

export const { setUser } = userSlice.actions
export default userSlice.reducer
