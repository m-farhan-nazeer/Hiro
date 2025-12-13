import { useEffect, useCallback, useMemo } from 'react'
import Avatar from '@/components/ui/Avatar'
import Badge from '@/components/ui/Badge'
import DataTable from '@/components/shared/DataTable'
import Select from '@/components/ui/Select'
import {
    getApplications,
    updateApplicationStatus,
    setTableData,
    setSelectedCustomer,
    setDrawerOpen,
    useAppDispatch,
    useAppSelector,
    Customer,
    Application
} from '../store'
import useThemeClass from '@/utils/hooks/useThemeClass'
import CustomerEditDialog from './CustomerEditDialog'
import { Link } from 'react-router-dom'
import dayjs from 'dayjs'
import cloneDeep from 'lodash/cloneDeep'
import type { OnSortParam, ColumnDef } from '@/components/shared/DataTable'
import type { SingleValue } from 'react-select'

const statusColor: Record<string, string> = {
    hired: 'bg-emerald-500',
    shortlisted: 'bg-blue-500',
    pending: 'bg-yellow-500',
    rejected: 'bg-red-500',
    Hired: 'bg-emerald-500',
    Shortlisted: 'bg-blue-500',
    Pending: 'bg-yellow-500',
    Rejected: 'bg-red-500',
}

const ActionColumn = ({ row }: { row: Customer }) => {
    const { textTheme } = useThemeClass()
    const dispatch = useAppDispatch()

    const onEdit = () => {
        dispatch(setDrawerOpen())
        dispatch(setSelectedCustomer(row))
    }

    return (
        <div
            className={`${textTheme} cursor-pointer select-none font-semibold`}
            onClick={onEdit}
        >
            Edit
        </div>
    )
}

const NameColumn = ({ row }: { row: Customer }) => {
    const { textTheme } = useThemeClass()

    return (
        <div className="flex items-center">
            <Avatar size={28} shape="circle" src={row.img} />
            <Link
                className={`hover:${textTheme} ml-2 rtl:mr-2 font-semibold`}
                to={`/app/crm/customer-details?id=${row.id}`}
            >
                {row.name}
            </Link>
        </div>
    )
}

type CustomersTableProps = {
    jobId?: string | null
}

type StatusOption = {
    value: string
    label: string
}

const statusOptions: StatusOption[] = [
    { value: 'pending', label: 'Pending' },
    { value: 'shortlisted', label: 'Shortlisted' },
    { value: 'hired', label: 'Hired' },
    { value: 'rejected', label: 'Rejected' },
]

const Customers = ({ jobId }: CustomersTableProps = {}) => {
    const dispatch = useAppDispatch()
    const data = useAppSelector((state) => state.crmCustomers.data.applicationList)
    const loading = useAppSelector((state) => state.crmCustomers.data.loading)
    const filterData = useAppSelector(
        (state) => state.crmCustomers.data.filterData
    )

    const { pageIndex, pageSize, sort, query, total } = useAppSelector(
        (state) => state.crmCustomers.data.tableData
    )

    const fetchData = useCallback(() => {
        dispatch(getApplications({ 
            jobId: jobId ? Number(jobId) : undefined, 
            status: filterData.status 
        }))
    }, [dispatch, jobId, filterData.status])

    const handleStatusChange = useCallback((applicationId: number, newStatus: string) => {
        dispatch(updateApplicationStatus({ 
            id: applicationId, 
            status: newStatus,
            jobId: jobId ? Number(jobId) : undefined,
            currentStatus: filterData.status
        })).then(() => {
            // Refresh the list after update to get latest data
            dispatch(getApplications({ 
                jobId: jobId ? Number(jobId) : undefined, 
                status: filterData.status 
            }))
        }).catch((error) => {
            console.error('Failed to update application status:', error)
        })
    }, [dispatch, jobId, filterData.status])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    const tableData = useMemo(
        () => ({ pageIndex, pageSize, sort, query, total }),
        [pageIndex, pageSize, sort, query, total]
    )

    const columns: ColumnDef<Application>[] = useMemo(
        () => [
            {
                header: 'Name',
                accessorKey: 'applicant_name',
            },
            {
                header: 'Email',
                accessorKey: 'applicant_email',
            },
            {
                header: 'Job Title',
                accessorKey: 'job_title',
            },
            {
                header: 'Status',
                accessorKey: 'status',
                cell: (props) => {
                    const row = props.row.original
                    const status = row.status || 'pending'
                    const currentOption = statusOptions.find(opt => opt.value === status) || statusOptions[0]
                    
                    return (
                        <div className="flex items-center gap-2">
                            {/* <Badge className={statusColor[status] || statusColor.pending} /> */}
                            <Select<StatusOption>
                                size="sm"
                                className="min-w-[120px]"
                                value={currentOption}
                                options={statusOptions}
                                onChange={(option: SingleValue<StatusOption>) => {
                                    if (option && option.value !== status) {
                                        handleStatusChange(row.id, option.value)
                                    }
                                }}
                            />
                        </div>
                    )
                },
            },
            {
                header: 'Score',
                accessorKey: 'score',
                cell: (props) => {
                    const row = props.row.original
                    return <span>{row.score || 'N/A'}</span>
                },
            },
            {
                header: 'Date',
                accessorKey: 'date',
                cell: (props) => {
                    const row = props.row.original
                    return (
                        <div className="flex items-center">
                            {dayjs(row.date).format('MM/DD/YYYY')}
                        </div>
                    )
                },
            },
            {
                header: 'Resume',
                accessorKey: 'has_resume',
                cell: (props) => {
                    const row = props.row.original
                    if (row.has_resume && row.resume_url) {
                        return (
                            <a
                                href={row.resume_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:underline"
                            >
                                View Resume
                            </a>
                        )
                    }
                    return <span className="text-gray-400">No Resume</span>
                },
            },
            // {
            //     header: 'Last online',
            //     accessorKey: 'lastOnline',
            //     cell: (props) => {
            //         const row = props.row.original
            //         return (
            //             <div className="flex items-center">
            //                 {dayjs.unix(row.lastOnline).format('MM/DD/YYYY')}
            //             </div>
            //         )
            //     },
            // },
            // {
            //     header: '',
            //     id: 'action',
            //     cell: (props) => <ActionColumn row={props.row.original} />,
            // },
        ],
        []
    )

    const onPaginationChange = (page: number) => {
        const newTableData = cloneDeep(tableData)
        newTableData.pageIndex = page
        dispatch(setTableData(newTableData))
    }

    const onSelectChange = (value: number) => {
        const newTableData = cloneDeep(tableData)
        newTableData.pageSize = Number(value)
        newTableData.pageIndex = 1
        dispatch(setTableData(newTableData))
    }

    const onSort = (sort: OnSortParam) => {
        const newTableData = cloneDeep(tableData)
        newTableData.sort = sort
        dispatch(setTableData(newTableData))
    }

    return (
        <>
            <DataTable
                columns={columns}
                data={data}
                skeletonAvatarColumns={[0]}
                skeletonAvatarProps={{ width: 28, height: 28 }}
                loading={loading}
                pagingData={{
                    total: tableData.total as number,
                    pageIndex: tableData.pageIndex as number,
                    pageSize: tableData.pageSize as number,
                }}
                onPaginationChange={onPaginationChange}
                onSelectChange={onSelectChange}
                onSort={onSort}
            />
            <CustomerEditDialog />
        </>
    )
}

export default Customers
