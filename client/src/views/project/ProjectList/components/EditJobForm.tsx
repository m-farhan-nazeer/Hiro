import { useState } from 'react'
import { FormItem, FormContainer } from '@/components/ui/Form'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import { Field, Form, Formik, FieldProps } from 'formik'
import { updateJob } from '@/services/JobServices'
import CreatableSelect from 'react-select/creatable'
import { SKILL_OPTIONS } from '@/constants/skills.constant'
import * as Yup from 'yup'
import './hide-scrollbar.css'

type JobData = {
    id: number;
    title: string;
    description: string;
    status: string;
    jobtype: string;
    jobtime: string;
    required_skills: string;
    domain: string;
}

type FormModel = {
    title: string
    status: string
    domain: string
    description: string
    jobType: string
    jobTime: string
    requiredSkills: string[]
}

type EditJobFormProps = {
    job: JobData;
    onClose: () => void;
    onJobUpdated?: () => void;
}

const validationSchema = Yup.object().shape({
    title: Yup.string().min(3, 'Too Short!').required('Title required'),
    status: Yup.string().oneOf(['active', 'closed']).required('Status required'),
    domain: Yup.string().min(3, 'Too Short!').required('Domain required'),
    description: Yup.string().required('Description required'),
    jobType: Yup.string().oneOf(['remote', 'onsite']).required('Job type required'),
    jobTime: Yup.string().oneOf(['part-time', 'full-time']).required('Job time required'),
    requiredSkills: Yup.array().of(Yup.string()).min(1, 'At least one skill required'),
})

const EditJobForm = ({ job, onClose, onJobUpdated }: EditJobFormProps) => {
    const [isSubmitting, setIsSubmitting] = useState(false)

    const statusOptions = [
        { value: 'active', label: 'Active' },
        { value: 'closed', label: 'Closed' },
    ];
    const jobTypeOptions = [
        { value: 'remote', label: 'Remote' },
        { value: 'onsite', label: 'Onsite' },
    ];
    const jobTimeOptions = [
        { value: 'part-time', label: 'Part-time' },
        { value: 'full-time', label: 'Full-time' },
    ];
    const skillOptions = SKILL_OPTIONS;

    // Parse the required_skills string into an array
    const initialSkills = job.required_skills ? job.required_skills.split(',').map(s => s.trim()) : [];

    const onSubmit = async (formValue: FormModel) => {
        setIsSubmitting(true)

        try {
            const { title, status, domain, description, jobType, jobTime, requiredSkills } = formValue

            const jobData = {
                title,
                description,
                status,
                jobtype: jobType,
                jobtime: jobTime,
                required_skills: requiredSkills.join(', '),
                domain,
            }

            await updateJob(job.id, jobData)
            onJobUpdated?.()
            onClose()
        } catch (error) {
            console.error('Failed to update job:', error)
            // Handle error - you might want to show a toast notification here
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Formik
            initialValues={{
                title: job.title,
                status: job.status,
                domain: job.domain,
                description: job.description,
                jobType: job.jobtype,
                jobTime: job.jobtime,
                requiredSkills: initialSkills,
            }}
            validationSchema={validationSchema}
            onSubmit={onSubmit}
        >
            {({ touched, errors, values }) => (
                <Form
                    style={{
                        overflowY: 'auto',
                        maxHeight: '80vh',
                        paddingTop: '16px',
                        paddingBottom: '16px',
                        scrollbarWidth: 'none',
                        msOverflowStyle: 'none',
                    }}
                    className="hide-scrollbar"
                >
                    <FormContainer>
                        <FormItem
                            label="Title"
                            invalid={errors.title && touched.title}
                            errorMessage={errors.title}
                        >
                            <Field
                                type="text"
                                autoComplete="off"
                                name="title"
                                placeholder="Enter title"
                                component={Input}
                            />
                        </FormItem>
                        <FormItem
                            label="Status"
                            invalid={Boolean(errors.status) && Boolean(touched.status)}
                            errorMessage={typeof errors.status === 'string' ? errors.status : undefined}
                        >
                            <Field name="status">
                                {({ field, form }: FieldProps) => (
                                    <Select
                                        className="min-w-[120px]"
                                        options={statusOptions}
                                        value={statusOptions.find(opt => opt.value === field.value)}
                                        onChange={option => form.setFieldValue(field.name, option ? option.value : '')}
                                    />
                                )}
                            </Field>
                        </FormItem>
                        <FormItem
                            label="Domain"
                            invalid={errors.domain && touched.domain}
                            errorMessage={errors.domain}
                        >
                            <Field
                                type="text"
                                autoComplete="off"
                                name="domain"
                                placeholder="Enter domain"
                                component={Input}
                            />
                        </FormItem>
                        <FormItem
                            label="Job Type"
                            invalid={errors.jobType && touched.jobType}
                            errorMessage={errors.jobType}
                        >
                            <Field name="jobType">
                                {({ field, form }: FieldProps) => (
                                    <Select
                                        className="min-w-[120px]"
                                        options={jobTypeOptions}
                                        value={jobTypeOptions.find(opt => opt.value === field.value)}
                                        onChange={option => form.setFieldValue(field.name, option ? option.value : '')}
                                    />
                                )}
                            </Field>
                        </FormItem>
                        <FormItem
                            label="Job Time"
                            invalid={errors.jobTime && touched.jobTime}
                            errorMessage={errors.jobTime}
                        >
                            <Field name="jobTime">
                                {({ field, form }: FieldProps) => (
                                    <Select
                                        className="min-w-[120px]"
                                        options={jobTimeOptions}
                                        value={jobTimeOptions.find(opt => opt.value === field.value)}
                                        onChange={option => form.setFieldValue(field.name, option ? option.value : '')}
                                    />
                                )}
                            </Field>
                        </FormItem>
                        <FormItem
                            label="Required Skills"
                            invalid={Boolean(errors.requiredSkills) && Boolean(touched.requiredSkills)}
                            errorMessage={typeof errors.requiredSkills === 'string' ? errors.requiredSkills : undefined}
                        >
                            <Field name="requiredSkills">
                                {({ field, form }: FieldProps) => (
                                    <Select
                                        isMulti
                                        componentAs={CreatableSelect}
                                        className="min-w-[120px]"
                                        options={skillOptions}
                                        value={skillOptions.filter(opt => field.value.includes(opt.value)).concat(
                                            field.value.filter((val: string) => !skillOptions.find(opt => opt.value === val))
                                                .map((val: string) => ({ value: val, label: val }))
                                        )}
                                        onChange={option => form.setFieldValue(field.name, Array.isArray(option) ? option.map((o: any) => o.value) : [])}
                                    />
                                )}
                            </Field>
                        </FormItem>
                        <FormItem
                            label="Job Description"
                            invalid={errors.description && touched.description}
                            errorMessage={errors.description}
                        >
                            <Field
                                textArea
                                type="text"
                                autoComplete="off"
                                name="description"
                                placeholder="Enter Job Description"
                                component={Input}
                            />
                        </FormItem>
                        <div className="flex gap-2">
                            <Button
                                block
                                variant="solid"
                                type="submit"
                                loading={isSubmitting}
                                disabled={isSubmitting}
                            >
                                Update Job
                            </Button>
                            <Button
                                block
                                variant="plain"
                                type="button"
                                onClick={onClose}
                            >
                                Cancel
                            </Button>
                        </div>
                    </FormContainer>
                </Form>
            )}
        </Formik>
    )
}

export default EditJobForm
