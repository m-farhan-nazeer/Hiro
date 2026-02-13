import DatePicker from '@/components/ui/DatePicker'
import Button from '@/components/ui/Button'
import {
    setStartDate,
    setEndDate,
    getSalesDashboardData,
    useAppSelector,
} from '../store'
import { useAppDispatch } from '@/store'
import { HiOutlineFilter, HiOutlineBriefcase, HiOutlineUser } from 'react-icons/hi'
import dayjs from 'dayjs'
import Avatar from '@/components/ui/Avatar'

const dateFormat = 'MMM DD, YYYY'
const { DatePickerRange } = DatePicker

const SalesDashboardHeader = () => {
    const dispatch = useAppDispatch()

    const { userName, displayName, avatar, title } = useAppSelector((state) => state.auth.user)

    const startDate = useAppSelector(
        (state) => state.salesDashboard.data.startDate
    )
    const endDate = useAppSelector((state) => state.salesDashboard.data.endDate)

    const handleDateChange = (value: [Date | null, Date | null]) => {
        dispatch(setStartDate(dayjs(value[0]).unix()))
        dispatch(setEndDate(dayjs(value[1]).unix()))
    }

    const onFilter = () => {
        dispatch(getSalesDashboardData())
    }

    return (
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-4 gap-4">
            <div className="flex items-center gap-4">
                <Avatar
                    size={65}
                    shape="circle"
                    src={avatar}
                    icon={<HiOutlineUser />}
                    className="border-2 border-white dark:border-gray-800 shadow-md"
                />
                <div>
                    <h3 className="font-bold">Welcome back, {displayName || userName}!</h3>
                    <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                        <HiOutlineBriefcase className="text-lg" />
                        <span className="font-medium">{title || 'Member'}</span>
                    </div>
                </div>
            </div>

        </div>
    )
}

export default SalesDashboardHeader
