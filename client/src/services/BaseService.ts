import axios from 'axios'
import appConfig from '@/configs/app.config'
import { PERSIST_STORE_NAME } from '@/constants/app.constant'
import deepParseJson from '@/utils/deepParseJson'
import store, { signOutSuccess } from '../store'

// Django backend base URL — configurable via VITE_API_URL for production deployments
const BACKEND_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const BaseService = axios.create({
    timeout: 60000,
    baseURL: BACKEND_BASE_URL + appConfig.apiPrefix, // Points to http://127.0.0.1:8000/api
    withCredentials: true, // Include session cookies for Django
    headers: {},
})

// Response interceptor to handle 401/403 errors
BaseService.interceptors.response.use(
    (response) => response,
    (error) => {
        const { response } = error

        // If session is invalid/missing, clear auth state so app redirects to sign-in.
        const isMissingAuthCredentials =
            response?.status === 403 &&
            typeof response?.data?.detail === 'string' &&
            response.data.detail
                .toLowerCase()
                .includes('authentication credentials were not provided')

        if (response && (response.status === 401 || isMissingAuthCredentials)) {
            store.dispatch(signOutSuccess())
        }

        return Promise.reject(error)
    }
)

export default BaseService
