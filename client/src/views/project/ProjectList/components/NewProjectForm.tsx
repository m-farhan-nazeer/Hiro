import { useState, useEffect } from 'react'
import { FormItem, FormContainer } from '@/components/ui/Form'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import Avatar from '@/components/ui/Avatar'
import hooks from '@/components/ui/hooks'
import NewTaskField from './NewTaskField'
import { Field, Form, Formik, FieldProps } from 'formik'
import { HiCheck } from 'react-icons/hi'
import { components, MultiValueGenericProps, OptionProps } from 'react-select'
import {
    getMembers,
    putProject,
    toggleNewProjectDialog,
    useAppDispatch,
    useAppSelector,
} from '../store'
import { createJob } from '@/services/JobServices'
import { APP_PREFIX_PATH } from '@/constants/route.constant'
import cloneDeep from 'lodash/cloneDeep'
import * as Yup from 'yup'
import { auto } from '@popperjs/core'
import './hide-scrollbar.css'

type FormModel = {
    title: string
    status: string
    domain: string
    description: string
    jobType: string
    jobTime: string
    requiredSkills: string[]
    assignees: {
        img: string
        name: string
        label: string
    }[]
}

type TaskCount = {
    completedTask?: number
    totalTask?: number
}

const { MultiValueLabel } = components

const { useUniqueId } = hooks

const CustomSelectOption = ({
    innerProps,
    label,
    data,
    isSelected,
}: OptionProps<{ img: string }>) => {
    return (
        <div
            className={`flex items-center justify-between p-2 ${isSelected
                ? 'bg-gray-100 dark:bg-gray-500'
                : 'hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
            {...innerProps}
        >
            <div className="flex items-center">
                <Avatar shape="circle" size={20} src={data.img} />
                <span className="ml-2 rtl:mr-2">{label}</span>
            </div>
            {isSelected && <HiCheck className="text-emerald-500 text-xl" />}
        </div>
    )
}

const CustomControlMulti = ({ children, ...props }: MultiValueGenericProps) => {
    const { img } = props.data

    return (
        <MultiValueLabel {...props}>
            <div className="inline-flex items-center">
                <Avatar
                    className="mr-2 rtl:ml-2"
                    shape="circle"
                    size={15}
                    src={img}
                />
                {children}
            </div>
        </MultiValueLabel>
    )
}

// Validation schema - status is only required in edit mode
const getValidationSchema = (isEditMode: boolean) => Yup.object().shape({
    title: Yup.string().min(3, 'Too Short!').required('Title required'),
    status: isEditMode
        ? Yup.string().oneOf(['active', 'closed']).required('Status required')
        : Yup.string().oneOf(['active', 'closed']),
    domain: Yup.string().min(3, 'Too Short!').required('Domain required'),
    description: Yup.string().required('Description required'),
    // assignees: Yup.array().min(1, 'Assignee required'),
    jobType: Yup.string().oneOf(['remote', 'onsite']).required('Job type required'),
    jobTime: Yup.string().oneOf(['part-time', 'full-time']).required('Job time required'),
    requiredSkills: Yup.array().of(Yup.string()).min(1, 'At least one skill required'),
    rememberMe: Yup.bool(),
})

type NewProjectFormProps = {
    onJobUpdated?: () => void;
    isEditMode?: boolean;
    initialData?: Partial<FormModel>;
}

const NewProjectForm = ({ onJobUpdated, isEditMode = false, initialData }: NewProjectFormProps) => {
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
    const skillOptions = [
        { value: 'JavaScript', label: 'JavaScript' },
        { value: 'Python', label: 'Python' },
        { value: 'React', label: 'React' },
        { value: 'Django', label: 'Django' },
        { value: 'SQL', label: 'SQL' },
        { value: 'Node.js', label: 'Node.js' },
        // Add more skills as needed
    ];
    const dispatch = useAppDispatch()

    const members = useAppSelector((state) => state.projectList.data.allMembers)

    const newId = useUniqueId('project-')

    const [taskCount, setTaskCount] = useState<TaskCount>({})

    useEffect(() => {
        dispatch(getMembers())
    }, [dispatch])

    const handleAddNewTask = (count: TaskCount) => {
        setTaskCount(count)
    }

    const onSubmit = async (
        formValue: FormModel,
        setSubmitting: (isSubmitting: boolean) => void
    ) => {
        setSubmitting(true)

        try {
            const { title, status, domain, description, assignees, jobType, jobTime, requiredSkills } = formValue
            const { totalTask, completedTask } = taskCount
            const member = cloneDeep(assignees).map((assignee) => {
                assignee.name = assignee.label
                return assignee
            })

            // Create job via API
            const jobData = {
                title,
                description,
                status,
                jobtype: jobType,
                jobtime: jobTime,
                required_skills: requiredSkills.join(', '),
                domain,
            }

            const createdJob = await createJob(jobData)

            // Create application link for this job and copy to clipboard
            try {
                const appLink = `${window.location.origin}/apply?id=${createdJob.id}`
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(appLink)
                    // eslint-disable-next-line no-alert
                    alert('Job created. Application link copied to clipboard')
                } else {
                    // fallback prompt
                    // eslint-disable-next-line no-alert
                    prompt('Job created. Copy application link', appLink)
                }
            } catch (err) {
                // ignore clipboard errors but still continue
                console.warn('Failed to copy application link', err)
            }

            // Refresh the jobs list
            onJobUpdated?.()

            // Also update the local state for consistency
            const values = {
                id: newId,
                name: title,
                status: status,
                domain: domain,
                desc: description,
                jobType,
                jobTime,
                requiredSkills,
                totalTask,
                completedTask,
                progression:
                    ((completedTask as number) / (totalTask as number)) * 100 || 0,
                member,
            }
            dispatch(putProject(values))
            dispatch(toggleNewProjectDialog(false))
        } catch (error) {
            console.error('Failed to create job:', error)
            // Handle error - you might want to show a toast notification here
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <Formik
            initialValues={{
                title: initialData?.title || '',
                status: initialData?.status || 'active', // Default to 'active' for new jobs
                domain: initialData?.domain || '',
                description: initialData?.description || '',
                jobType: initialData?.jobType || '',
                jobTime: initialData?.jobTime || '',
                requiredSkills: initialData?.requiredSkills || [],
                assignees: initialData?.assignees || [],
            }}
            validationSchema={getValidationSchema(isEditMode)}
            onSubmit={(values, { setSubmitting }) => {
                onSubmit(values, setSubmitting)
            }}
        >
            {({ touched, errors, values }) => (
                <Form
                    style={{
                        overflowY: 'auto',
                        maxHeight: '80vh',
                        // marginTop: '32px',
                        // marginBottom: '32px',
                        paddingTop: '16px',
                        paddingBottom: '16px',
                        scrollbarWidth: 'none', // Firefox
                        msOverflowStyle: 'none', // IE 10+
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
                        {/* Status field only shown in edit mode */}
                        {isEditMode && (
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
                        )}
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
                                        className="min-w-[120px]"
                                        options={skillOptions}
                                        value={skillOptions.filter(opt => field.value.includes(opt.value))}
                                        onChange={option => form.setFieldValue(field.name, Array.isArray(option) ? option.map((o: any) => o.value) : [])}
                                    />
                                )}
                            </Field>
                        </FormItem>

                        {/* <FormItem
                            label="Assignees"
                            invalid={
                                (errors.assignees && touched.assignees) as ''
                            }
                            errorMessage={errors.assignees as string}
                        >
                            <Field name="assignees">
                                {({ field, form }: FieldProps) => (
                                    <Select
                                        isMulti
                                        className="min-w-[120px]"
                                        components={{
                                            Option: CustomSelectOption,
                                            MultiValueLabel: CustomControlMulti,
                                        }}
                                        field={field}
                                        form={form}
                                        options={members}
                                        value={values.assignees}
                                        onChange={(option) => {
                                            form.setFieldValue(
                                                field.name,
                                                option
                                            )
                                        }}
                                    />
                                )}
                            </Field>
                        </FormItem> */}
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
                        {/* <NewTaskField onAddNewTask={handleAddNewTask} /> */}
                        <Button block variant="solid" type="submit">
                            {isEditMode ? 'Update' : 'Post'}
                        </Button>
                    </FormContainer>
                </Form>
            )}
        </Formik>
    )
}

export default NewProjectForm
