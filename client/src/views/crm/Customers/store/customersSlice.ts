import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
    apiGetCrmCustomers,
    apPutCrmCustomer,
    apiGetCrmCustomersStatistic,
} from '@/services/CrmService'
import { listApplications, updateApplication } from '@/services/ApplicationService'
import type { TableQueries } from '@/@types/common'

type PersonalInfo = {
    location: string
    title: string
    birthday: string
    phoneNumber: string
    facebook: string
    twitter: string
    pinterest: string
    linkedIn: string
}

type OrderHistory = {
    id: string
    item: string
    status: string
    amount: number
    date: number
}

type PaymentMethod = {
    cardHolderName: string
    cardType: string
    expMonth: string
    expYear: string
    last4Number: string
    primary: boolean
}

type Subscription = {
    plan: string
    status: string
    billing: string
    nextPaymentDate: number
    amount: number
}

export type Applicant = {
    id: number
    name: string
    email: string
    telephone: string
    prior_experience?: string
    source?: string
    skill_set?: string
    status?: string | null
    score?: string | null
    jobAppliedFor?: string | null
    appliedDate?: string | null
    has_resume?: boolean
    resume_url?: string | null
}

export type Application = {
    id: number
    applicant: number
    applicant_name: string
    applicant_email: string
    job: number
    job_title: string
    score: string | null
    scoring_status: 'pending' | 'processing' | 'completed' | 'failed'
    status: string
    date: string
    has_resume: boolean
    resume_url: string | null
}

export type Customer = {
    id: string
    name: string
    email: string
    img: string
    role: string
    lastOnline: number
    status: string
    personalInfo: PersonalInfo
    orderHistory: OrderHistory[]
    paymentMethod: PaymentMethod[]
    subscription: Subscription[]
}

type Statistic = {
    value: number
    growShrink: number
}

type CustomerStatistic = {
    totalCustomers: Statistic
    activeCustomers: Statistic
    newCustomers: Statistic
}

type Filter = {
    status: string
}

type GetCrmCustomersResponse = {
    // data: Customer[]
    data: Applicant[]
    total: number
}

type GetApplicantsResponse = {
    data: Applicant[]
    total: number
}

type GetCrmCustomersStatisticResponse = CustomerStatistic

export type CustomersState = {
    loading: boolean
    statisticLoading: boolean
    // customerList: Customer[]
    applicantList: Applicant[]
    applicationList: Application[]
    statisticData: Partial<CustomerStatistic>
    tableData: TableQueries
    filterData: Filter
    drawerOpen: boolean
    selectedApplicant: Partial<Applicant>
}

export const SLICE_NAME = 'crmCustomers'

export const getCustomerStatistic = createAsyncThunk(
    'crmCustomers/data/getCustomerStatistic',
    async () => {
        const response =
            await apiGetCrmCustomersStatistic<GetCrmCustomersStatisticResponse>()
        return response.data
    }
)

export const getCustomers = createAsyncThunk(
    'crmCustomers/data/getCustomers',
    async (data: TableQueries & { filterData?: Filter }) => {
        const response = await apiGetCrmCustomers<
            GetCrmCustomersResponse,
            TableQueries
        >(data)
        return response.data
    }
)

export const getApplications = createAsyncThunk(
    'crmCustomers/data/getApplications',
    async (params?: { jobId?: string | number; status?: string; silent?: boolean }) => {
        const jobId = params?.jobId
        const status = params?.status
        const applications = await listApplications(jobId, status)
        return { applications: applications as Application[], silent: params?.silent }
    }
)

export const updateApplicationStatus = createAsyncThunk(
    'crmCustomers/data/updateApplicationStatus',
    async (params: { id: number; status: string; jobId?: string | number; currentStatus?: string }) => {
        await updateApplication(params.id, { status: params.status })
        return { id: params.id, status: params.status }
    }
)

export const putCustomer = createAsyncThunk(
    'crmCustomers/data/putCustomer',
    async (data: Customer) => {
        const response = await apPutCrmCustomer(data)
        return response.data
    }
)

export const initialTableData: TableQueries = {
    total: 0,
    pageIndex: 1,
    pageSize: 10,
    query: '',
    sort: {
        order: '',
        key: '',
    },
}

export const initialFilterData = {
    status: '',
}

const initialState: CustomersState = {
    loading: false,
    statisticLoading: false,
    // customerList: [],
    applicantList: [],
    applicationList: [],
    statisticData: {},
    tableData: initialTableData,
    filterData: initialFilterData,
    drawerOpen: false,
    selectedApplicant: {},
}

const customersSlice = createSlice({
    name: `${SLICE_NAME}/state`,
    initialState,
    reducers: {
        setTableData: (state, action) => {
            state.tableData = action.payload
        },
        setCustomerList: (state, action) => {
            // state.customerList = action.payload
            state.applicantList = action.payload
        },
        setFilterData: (state, action) => {
            state.filterData = action.payload
        },
        setSelectedCustomer: (state, action) => {
            state.selectedApplicant = action.payload
        },
        setDrawerOpen: (state) => {
            state.drawerOpen = true
        },
        setDrawerClose: (state) => {
            state.drawerOpen = false
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(getCustomers.fulfilled, (state, action) => {
                state.applicantList = action.payload.data
                state.tableData.total = action.payload.total
                state.loading = false
            })
            .addCase(getCustomers.pending, (state) => {
                state.loading = true
            })
            .addCase(getCustomerStatistic.fulfilled, (state, action) => {
                state.statisticData = action.payload
                state.statisticLoading = false
            })
            .addCase(getCustomerStatistic.pending, (state) => {
                state.statisticLoading = true
            })
            .addCase(getApplications.fulfilled, (state, action) => {
                state.applicationList = action.payload.applications
                state.tableData.total = action.payload.applications.length
                state.loading = false
            })
            .addCase(getApplications.pending, (state, action) => {
                const isSilent = action.meta.arg?.silent
                if (!isSilent) {
                    state.loading = true
                }
            })
            .addCase(updateApplicationStatus.fulfilled, (state, action) => {
                // Update the application in the list
                const index = state.applicationList.findIndex(app => app.id === action.payload.id)
                if (index !== -1) {
                    state.applicationList[index].status = action.payload.status
                }
                state.loading = false
            })
            .addCase(updateApplicationStatus.pending, (state) => {
                state.loading = true
            })
    },
})

export const {
    setTableData,
    setCustomerList,
    setFilterData,
    setSelectedCustomer,
    setDrawerOpen,
    setDrawerClose,
} = customersSlice.actions

export default customersSlice.reducer
