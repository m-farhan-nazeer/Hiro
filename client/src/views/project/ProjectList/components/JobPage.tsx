import AdaptableCard from '@/components/shared/AdaptableCard'
import CustomersTable from '../../../crm/Customers/components/CustomersTable'
import CustomersTableTools from '../../../crm/Customers/components/CustomersTableTools'
import { injectReducer } from '@/store'
import reducer from '../../../crm/Customers/store'

injectReducer('crmCustomers', reducer)

const Applicants = () => {
    return (
        <>
            <h2 className="mb-4">Applicants for job xyz </h2>
            <AdaptableCard className="h-full" bodyClass="h-full">
                <CustomersTableTools />
                <CustomersTable />
            </AdaptableCard>
        </>
    )
}

export default Applicants
