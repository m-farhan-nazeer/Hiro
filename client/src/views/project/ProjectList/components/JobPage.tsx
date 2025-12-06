import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { APP_PREFIX_PATH } from '@/constants/route.constant'
import Button from '@/components/ui/Button'
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
    const navigate = useNavigate()
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

    const openApplicationForm = () => {
        if (!jobId) return
        navigate(`${APP_PREFIX_PATH}/applications?id=${jobId}`)
    }

    const copyApplicationLink = async () => {
        if (!jobId) return
        const link = `${window.location.origin}${APP_PREFIX_PATH}/applications?id=${jobId}`
        try {
            await navigator.clipboard.writeText(link)
            // small confirmation
            // eslint-disable-next-line no-alert
            alert('Application link copied to clipboard')
        } catch (err) {
            // fallback: open a prompt so user can copy
            // eslint-disable-next-line no-alert
            prompt('Copy application link', link)
        }
    }

    return (
        <>
            <div className="flex items-center justify-between mb-4">
                <h2>
                    {jobId ? `Applicants for ${jobTitle || 'Loading...'}` : 'Applicants'}
                </h2>
                {jobId && (
                    <div className="flex items-center gap-2">
                        <Button size="sm" onClick={openApplicationForm}>Open Application Form</Button>
                        <Button size="sm" variant="plain" onClick={copyApplicationLink}>Copy Link</Button>
                    </div>
                )}
            </div>
            <AdaptableCard className="h-full" bodyClass="h-full">
                <CustomersTableTools jobId={jobId} />
                <CustomersTable jobId={jobId} />
            </AdaptableCard>
        </>
    )
}

export default Applicants
