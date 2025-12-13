import Select from '@/components/ui/Select'
import Badge from '@/components/ui/Badge'
import { setFilterData, useAppDispatch, useAppSelector, getApplications } from '../store'
import {
    components,
    ControlProps,
    OptionProps,
    SingleValue,
} from 'react-select'
import { HiCheck } from 'react-icons/hi'

type Option = {
    value: string
    label: string
    color: string
}

const { Control } = components

const options: Option[] = [
    { value: '', label: 'All', color: 'bg-gray-500' },
    { value: 'hired', label: 'Hired', color: 'bg-emerald-500' },
    { value: 'shortlisted', label: 'Shortlisted', color: 'bg-blue-500' },
    { value: 'pending', label: 'Pending', color: 'bg-yellow-500' },
    { value: 'rejected', label: 'Rejected', color: 'bg-red-500' },
]

const CustomSelectOption = ({
    innerProps,
    label,
    data,
    isSelected,
}: OptionProps<Option>) => {
    return (
        <div
            className={`flex items-center justify-between p-2 cursor-pointer ${
                isSelected
                    ? 'bg-gray-100 dark:bg-gray-500'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
            {...innerProps}
        >
            <div className="flex items-center gap-2">
                <Badge innerClass={data.color} />
                <span>{label}</span>
            </div>
            {isSelected && <HiCheck className="text-emerald-500 text-xl" />}
        </div>
    )
}

const CustomControl = ({ children, ...props }: ControlProps<Option>) => {
    const selected = props.getValue()[0]
    return (
        <Control {...props}>
            {selected && (
                <Badge
                    className="ltr:ml-4 rtl:mr-4"
                    innerClass={selected.color}
                />
            )}
            {children}
        </Control>
    )
}

type CustomerTableFilterProps = {
    jobId?: string | null
}

const CustomerTableFilter = ({ jobId }: CustomerTableFilterProps = {}) => {
    const dispatch = useAppDispatch()

    const { status } = useAppSelector(
        (state) => state.crmCustomers.data.filterData
    )

    const onStatusFilterChange = (selected: SingleValue<Option>) => {
        const newStatus = selected?.value || ''
        dispatch(setFilterData({ status: newStatus }))
        // Trigger refetch with new status
        dispatch(getApplications({ 
            jobId: jobId ? Number(jobId) : undefined, 
            status: newStatus 
        }))
    }

    return (
        <Select<Option>
            options={options}
            size="sm"
            className="mb-4 min-w-[130px]"
            components={{
                Option: CustomSelectOption,
                Control: CustomControl,
            }}
            value={options.filter((option) => option.value === status)}
            onChange={onStatusFilterChange}
        />
    )
}

export default CustomerTableFilter
