import { createServer } from 'miragejs'
import appConfig from '@/configs/app.config'
import { notificationListData, searchQueryPoolData } from './data/commonData'
import {
    projectList,
    scrumboardData,
    issueData,
    projectDashboardData,
} from './data/projectData'
import { usersData, userDetailData } from './data/usersData'
import { eventsData, mailData, crmDashboardData } from './data/crmData'
import {
    productsData,
    ordersData,
    orderDetailsData,
    salesDashboardData,
} from './data/salesData'
import {
    portfolioData,
    walletsData,
    marketData,
    transactionHistoryData,
    cryptoDashboardData,
} from './data/cryptoData'
import {
    settingData,
    settingIntergrationData,
    settingBillingData,
    invoiceData,
    logData,
    accountFormData,
} from './data/accountData'
import {
    helpCenterCategoriesData,
    helpCenterArticleListData,
} from './data/knowledgeBaseData'
import { signInUserData } from './data/authData'

import {
    commonFakeApi,
    projectFakeApi,
    crmFakeApi,
    salesFakeApi,
    accountFakeApi,
    cryptoFakeApi,
    authFakeApi,
    knowledgeBaseFakeApi,
} from './fakeApi'

import { applicantsData } from './data/hiroData'

const { apiPrefix } = appConfig

export function mockServer({ environment = 'test' }) {
    return createServer({
        environment,
        trackRequests: true, // Track requests for debugging
        seeds(server) {
            server.db.loadData({
                notificationListData,
                searchQueryPoolData,
                projectList,
                scrumboardData,
                issueData,
                usersData,
                userDetailData,
                eventsData,
                mailData,
                productsData,
                ordersData,
                orderDetailsData,
                settingData,
                settingIntergrationData,
                settingBillingData,
                invoiceData,
                logData,
                accountFormData,
                portfolioData,
                walletsData,
                marketData,
                transactionHistoryData,
                helpCenterCategoriesData,
                helpCenterArticleListData,
                signInUserData,
                salesDashboardData,
                crmDashboardData,
                projectDashboardData,
                cryptoDashboardData,
                applicantsData
            })
        },
        routes() {
            this.urlPrefix = ''
            this.namespace = ''
            
            // CRITICAL: Passthrough external URLs FIRST, before any route handlers
            // This ensures Django backend requests bypass Mirage entirely
            this.passthrough('http://127.0.0.1:8000/**')
            this.passthrough('http://localhost:8000/**')
            this.passthrough((request) => {
                const url = request.url || ''
                // Passthrough any external HTTP URLs
                if (url.startsWith('http://') || url.startsWith('https://')) {
                    return true
                }
                // Passthrough data URLs
                if (url.startsWith('data:')) {
                    return true
                }
                return false
            })
            
            // Now register mock API routes (these only handle /api/* requests)
            commonFakeApi(this, apiPrefix)
            projectFakeApi(this, apiPrefix)
            crmFakeApi(this, apiPrefix)
            salesFakeApi(this, apiPrefix)
            accountFakeApi(this, apiPrefix)
            authFakeApi(this, apiPrefix)
            cryptoFakeApi(this, apiPrefix)
            knowledgeBaseFakeApi(this, apiPrefix)
        },
    })
}
