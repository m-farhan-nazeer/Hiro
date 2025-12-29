import React, { useState } from 'react'
import { FormContainer, FormItem } from '@/components/ui/Form'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Alert from '@/components/ui/Alert'
import { createApplication } from '@/services/ApplicationService'
import useQuery from '@/utils/hooks/useQuery'
import { Formik, Form, Field, FieldProps } from 'formik'
import * as Yup from 'yup'

type ApplicantFormProps = {
    onSubmitted?: () => void
} & Record<string, any>

// Validation constants
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const SUPPORTED_FILE_TYPES = ['application/pdf']

// Validation schema using Yup
const validationSchema = Yup.object().shape({
    name: Yup.string()
        .required('Full name is required')
        .min(2, 'Name must be at least 2 characters')
        .max(100, 'Name must be less than 100 characters')
        .matches(
            /^[a-zA-Z\s'-]+$/,
            'Name can only contain letters, spaces, hyphens, and apostrophes'
        )
        .trim(),
    email: Yup.string()
        .required('Email address is required')
        .email('Please enter a valid email address (e.g., john@example.com)')
        .max(254, 'Email must be less than 254 characters'),
    resume: Yup.mixed()
        .required('Resume is required')
        .test('fileExists', 'Please upload your resume', (value) => {
            return value instanceof File
        })
        .test('fileType', 'Only PDF files are allowed', (value) => {
            if (!value) return true
            return value instanceof File && SUPPORTED_FILE_TYPES.includes(value.type)
        })
        .test('fileSize', 'File size must be less than 5MB', (value) => {
            if (!value) return true
            return value instanceof File && value.size <= MAX_FILE_SIZE
        }),
})

type FormValues = {
    name: string
    email: string
    resume: File | null
}

const ApplicantForm = ({ onSubmitted }: ApplicantFormProps) => {
    const query = useQuery()
    const jobParam = query.get('id') || query.get('job')
    const [submitError, setSubmitError] = useState<string | null>(null)
    const [submitSuccess, setSubmitSuccess] = useState(false)

    const initialValues: FormValues = {
        name: '',
        email: '',
        resume: null,
    }

    // Check if job ID is missing
    if (!jobParam) {
        return (
            <Alert showIcon type="danger" className="mb-4">
                <div>
                    <h5 className="font-semibold mb-1">Invalid Application Link</h5>
                    <p>Job ID is missing from the link. Please open the application from a valid job posting link.</p>
                </div>
            </Alert>
        )
    }

    const handleSubmit = async (
        values: FormValues,
        { setSubmitting, resetForm }: { setSubmitting: (isSubmitting: boolean) => void; resetForm: () => void }
    ) => {
        setSubmitError(null)
        setSubmitSuccess(false)

        try {
            await createApplication({
                name: values.name.trim(),
                email: values.email.trim().toLowerCase(),
                job: parseInt(jobParam, 10),
                resume_file: values.resume as File,
            })

            setSubmitSuccess(true)
            resetForm()
            onSubmitted?.()
        } catch (err: any) {
            console.error('Application submission error:', err)
            setSubmitError(err?.message || 'Failed to submit application. Please try again.')
        } finally {
            setSubmitting(false)
        }
    }

    if (submitSuccess) {
        return (
            <Alert showIcon type="success" className="mb-4">
                <div>
                    <h5 className="font-semibold mb-1">Application Submitted Successfully!</h5>
                    <p>Thank you for applying. We will review your application and get back to you soon.</p>
                </div>
            </Alert>
        )
    }

    return (
        <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={handleSubmit}
            validateOnBlur={true}
            validateOnChange={true}
        >
            {({ errors, touched, isSubmitting, setFieldValue, setFieldTouched }) => (
                <Form>
                    <FormContainer>
                        {submitError && (
                            <Alert showIcon type="danger" className="mb-4">
                                {submitError}
                            </Alert>
                        )}

                        <FormItem
                            label="Full Name"
                            invalid={Boolean(errors.name && touched.name)}
                            errorMessage={errors.name}
                        >
                            <Field name="name">
                                {({ field }: FieldProps) => (
                                    <Input
                                        type="text"
                                        autoComplete="name"
                                        placeholder="John Doe"
                                        invalid={Boolean(errors.name && touched.name)}
                                        {...field}
                                    />
                                )}
                            </Field>
                        </FormItem>

                        <FormItem
                            label="Email Address"
                            invalid={Boolean(errors.email && touched.email)}
                            errorMessage={errors.email}
                        >
                            <Field name="email">
                                {({ field }: FieldProps) => (
                                    <Input
                                        type="email"
                                        autoComplete="email"
                                        placeholder="john@example.com"
                                        invalid={Boolean(errors.email && touched.email)}
                                        {...field}
                                    />
                                )}
                            </Field>
                        </FormItem>

                        <FormItem
                            label="Resume (PDF only, max 5MB)"
                            invalid={Boolean(errors.resume && touched.resume)}
                            errorMessage={errors.resume as string}
                        >
                            <input
                                type="file"
                                accept=".pdf,application/pdf"
                                aria-label="resume-file"
                                className={`w-full p-2 border rounded-md ${errors.resume && touched.resume
                                        ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                                        : 'border-gray-300 dark:border-gray-600'
                                    }`}
                                onChange={(event) => {
                                    const file = event.currentTarget.files?.[0]
                                    setFieldValue('resume', file || null)
                                }}
                                onBlur={() => setFieldTouched('resume', true)}
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Accepted format: PDF. Maximum file size: 5MB
                            </p>
                        </FormItem>

                        <Button
                            type="submit"
                            block
                            variant="solid"
                            loading={isSubmitting}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Submitting...' : 'Submit Application'}
                        </Button>

                        <p className="text-xs text-gray-500 text-center mt-4">
                            By submitting this application, you agree to allow us to process your information for recruitment purposes.
                        </p>
                    </FormContainer>
                </Form>
            )}
        </Formik>
    )
}

export default ApplicantForm
