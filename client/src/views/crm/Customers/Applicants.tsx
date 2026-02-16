import AdaptableCard from '@/components/shared/AdaptableCard'
import CustomersTable from './components/CustomersTable'
import CustomersTableTools from './components/CustomersTableTools'
import CustomerStatistic from './components/CustomerStatistic'
import { injectReducer } from '@/store'
import reducer from './store'

injectReducer('crmCustomers', reducer)

const Applicants = () => {
    return (
        <>
            <CustomerStatistic />
            <AdaptableCard bodyClass="h-full">
                <CustomersTableTools />
                <CustomersTable />
            </AdaptableCard>
        </>
    )
}

export default Applicants
