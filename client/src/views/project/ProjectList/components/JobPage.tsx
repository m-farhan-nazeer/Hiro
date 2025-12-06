import { useEffect, useState } from 'react'
import AdaptableCard from '@/components/shared/AdaptableCard'
import CustomersTable from '../../../crm/Customers/components/CustomersTable'
import CustomersTableTools from '../../../crm/Customers/components/CustomersTableTools'
import { injectReducer } from '@/store'
import reducer from '../../../crm/Customers/store'
import useQuery from '@/utils/hooks/useQuery'
import { getJob } from '@/services/JobServices'

injectReducer('crmCustomers', reducer)

const Applicants = () => {
    const query = useQuery()
    const jobId = query.get('id')
    const [jobTitle, setJobTitle] = useState<string>('')

    useEffect(() => {
        const fetchJobTitle = async () => {
            if (jobId) {
                try {
                    const job = await getJob(jobId)
                    setJobTitle(job.title || 'Unknown Job')
                } catch (error) {
                    console.error('Failed to fetch job:', error)
                    setJobTitle('Unknown Job')
                }
            }
        }
        fetchJobTitle()
    }, [jobId])

    return (
        <>
            <h2 className="mb-4">
                {jobId ? `Applicants for ${jobTitle || 'Loading...'}` : 'Applicants'}
            </h2>
            <AdaptableCard className="h-full" bodyClass="h-full">
                <CustomersTableTools jobId={jobId} />
                <CustomersTable jobId={jobId} />
            </AdaptableCard>
        </>
    )
}

export default Applicants
