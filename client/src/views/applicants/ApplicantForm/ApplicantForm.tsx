import React, { useState, useRef } from 'react'
import { FormContainer, FormItem } from '@/components/ui/Form'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { createApplication } from '@/services/ApplicationService'
import useQuery from '@/utils/hooks/useQuery'

type ApplicantFormProps = {
    onSubmitted?: () => void
} & Record<string, any>


const ApplicantForm = ({ onSubmitted }: ApplicantFormProps) => {
    const query = useQuery()
    const jobParam = query.get('id') || query.get('job')
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const fileRef = useRef<HTMLInputElement | null>(null)

    const resetForm = () => {
        setName('')
        setEmail('')
        if (fileRef.current) fileRef.current.value = ''
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!name || !email) {
            alert('Please fill name and email')
            return
        }

        if (!jobParam) {
            alert('Job id missing from link. Please open application from job page.')
            return
        }

        const fileInput = fileRef.current
        const file = fileInput?.files?.[0]
        if (!file) {
            alert('Please attach your resume (PDF)')
            return
        }

        setSubmitting(true)
        try {
            await createApplication({
                name,
                email,
                job: parseInt(jobParam, 10),
                resume_file: file
            })
            alert('Application submitted successfully')
            resetForm()
            onSubmitted && onSubmitted()
        } catch (err: any) {
            console.error(err)
            alert(err?.message || 'Failed to submit application')
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <FormContainer>
                <FormItem label="Full Name">
                    <Input
                        type="text"
                        value={name}
                        onChange={(e: any) => setName(e.target.value)}
                        placeholder="John Doe"
                    />
                </FormItem>

                <FormItem label="Email">
                    <Input
                        type="email"
                        value={email}
                        onChange={(e: any) => setEmail(e.target.value)}
                        placeholder="john@example.com"
                    />
                </FormItem>

                {/* Job ID is provided via the application link (query string). */}

                <FormItem label="Resume (PDF)">
                    <input
                        ref={fileRef}
                        type="file"
                        accept="application/pdf"
                        aria-label="resume-file"
                    />
                </FormItem>

                <Button type="submit" block variant="solid" disabled={submitting}>
                    {submitting ? 'Submitting...' : 'Submit Application'}
                </Button>
            </FormContainer>
        </form>
    )
}

export default ApplicantForm
