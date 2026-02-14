import classNames from 'classnames'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Tag from '@/components/ui/Tag'
import Notification from '@/components/ui/Notification'
import toast from '@/components/ui/toast'
import { FormContainer } from '@/components/ui/Form'
import { apiChangePassword } from '@/services/AuthService'
import FormDesription from './FormDesription'
import FormRow from './FormRow'
import { Field, Form, Formik } from 'formik'
import isLastChild from '@/utils/isLastChild'
import {
    HiOutlineEye,
    HiOutlineEyeOff,
} from 'react-icons/hi'
import { useState } from 'react'
import * as Yup from 'yup'

type PasswordFormModel = {
    password: string
    newPassword: string
    confirmNewPassword: string
}

const validationSchema = Yup.object().shape({
    password: Yup.string().required('Password Required'),
    newPassword: Yup.string()
        .required('Enter your new password')
        .min(8, 'Minimum 8 characters')
        .matches(/[a-z]/, 'At least one lowercase letter')
        .matches(/[A-Z]/, 'At least one uppercase letter')
        .matches(/[0-9]/, 'At least one number')
        .matches(/[!@#$%^&*(),.?":{}|<>]/, 'At least one special character'),
    confirmNewPassword: Yup.string().oneOf(
        [Yup.ref('newPassword'), ''],
        'Password not match'
    ),
})

const Password = () => {
    const [pwVisible, setPwVisible] = useState(false)
    const [newPwVisible, setNewPwVisible] = useState(false)
    const [confirmPwVisible, setConfirmPwVisible] = useState(false)

    const onFormSubmit = async (
        values: PasswordFormModel,
        setSubmitting: (isSubmitting: boolean) => void
    ) => {
        const payload = {
            old_password: values.password,
            new_password: values.newPassword,
        }

        try {
            await apiChangePassword(payload)
            toast.push(<Notification title={'Password updated'} type="success" />, {
                placement: 'top-center',
            })
        } catch (err: any) {
            console.error('Password change error:', err)
            const errorMessage = err.response?.data?.old_password?.[0] || 'Failed to update password'
            toast.push(<Notification title={errorMessage} type="danger" />, {
                placement: 'top-center',
            })
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <>
            <Formik
                initialValues={{
                    password: '',
                    newPassword: '',
                    confirmNewPassword: '',
                }}
                validationSchema={validationSchema}
                onSubmit={(values, { setSubmitting }) => {
                    setSubmitting(true)
                    setTimeout(() => {
                        onFormSubmit(values, setSubmitting)
                    }, 1000)
                }}
            >
                {({ touched, errors, isSubmitting, resetForm }) => {
                    const validatorProps = { touched, errors }
                    return (
                        <Form>
                            <FormContainer>
                                <FormDesription
                                    title="Password"
                                    desc="Enter your current & new password to reset your password"
                                />
                                <FormRow
                                    name="password"
                                    label="Current Password"
                                    {...validatorProps}
                                >
                                    <Field
                                        type={pwVisible ? 'text' : 'password'}
                                        autoComplete="off"
                                        name="password"
                                        placeholder="Current Password"
                                        component={Input}
                                        suffix={
                                            <span
                                                className="cursor-pointer text-xl"
                                                onClick={() => setPwVisible(!pwVisible)}
                                            >
                                                {pwVisible ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                                            </span>
                                        }
                                    />
                                </FormRow>
                                <FormRow
                                    name="newPassword"
                                    label="New Password"
                                    {...validatorProps}
                                >
                                    <Field
                                        type={newPwVisible ? 'text' : 'password'}
                                        autoComplete="off"
                                        name="newPassword"
                                        placeholder="New Password"
                                        component={Input}
                                        suffix={
                                            <span
                                                className="cursor-pointer text-xl"
                                                onClick={() => setNewPwVisible(!newPwVisible)}
                                            >
                                                {newPwVisible ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                                            </span>
                                        }
                                    />
                                </FormRow>
                                <FormRow
                                    name="confirmNewPassword"
                                    label="Confirm Password"
                                    {...validatorProps}
                                >
                                    <Field
                                        type={confirmPwVisible ? 'text' : 'password'}
                                        autoComplete="off"
                                        name="confirmNewPassword"
                                        placeholder="Confirm Password"
                                        component={Input}
                                        suffix={
                                            <span
                                                className="cursor-pointer text-xl"
                                                onClick={() => setConfirmPwVisible(!confirmPwVisible)}
                                            >
                                                {confirmPwVisible ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                                            </span>
                                        }
                                    />
                                </FormRow>
                                <div className="mt-4 ltr:text-right">
                                    <Button
                                        className="ltr:mr-2 rtl:ml-2"
                                        type="button"
                                        onClick={() => resetForm()}
                                    >
                                        Reset
                                    </Button>
                                    <Button
                                        variant="solid"
                                        loading={isSubmitting}
                                        type="submit"
                                    >
                                        {isSubmitting
                                            ? 'Updating'
                                            : 'Update Password'}
                                    </Button>
                                </div>
                            </FormContainer>
                        </Form>
                    )
                }}
            </Formik>
        </>
    )
}

export default Password
