import axios from 'axios'
import appConfig from '@/configs/app.config'
import { PERSIST_STORE_NAME } from '@/constants/app.constant'
import deepParseJson from '@/utils/deepParseJson'
import store, { signOutSuccess } from '../store'

// Django backend base URL (dev)
const BACKEND_BASE_URL = 'http://127.0.0.1:8000'

const BaseService = axios.create({
    timeout: 60000,
    baseURL: BACKEND_BASE_URL + appConfig.apiPrefix, // Points to http://127.0.0.1:8000/api
    withCredentials: true, // Include session cookies for Django
    headers: {
        'Content-Type': 'application/json',
    },
})

// Response interceptor to handle 401/403 errors
BaseService.interceptors.response.use(
    (response) => response,
    (error) => {
        const { response } = error

        // If unauthorized/forbidden, clear auth state
        if (response && (response.status === 401 || response.status === 403)) {
            // Only clear if it's an auth-related endpoint
            if (response.config?.url?.includes('/users/')) {
                store.dispatch(signOutSuccess())
            }
        }

        return Promise.reject(error)
    }
)

export default BaseService
