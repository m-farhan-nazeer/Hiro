import Input from '@/components/ui/Input'
import Avatar from '@/components/ui/Avatar'
import Upload from '@/components/ui/Upload'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import Switcher from '@/components/ui/Switcher'
import Notification from '@/components/ui/Notification'
import toast from '@/components/ui/toast'
import { FormContainer } from '@/components/ui/Form'
import { apiUpdateAccountSettingData } from '@/services/AccountServices'
import { useAppSelector, useAppDispatch } from '@/store'
import { setUser } from '@/store/slices/auth/userSlice'
import FormDesription from './FormDesription'
import FormRow from './FormRow'
import { Field, Form, Formik } from 'formik'
import { components } from 'react-select'
import {
    HiOutlineUserCircle,
    HiOutlineMail,
    HiOutlineBriefcase,
    HiOutlineUser,
    HiCheck,
    HiOutlineGlobeAlt,
} from 'react-icons/hi'
import * as Yup from 'yup'
import type { OptionProps, ControlProps } from 'react-select'
import type { FormikProps, FieldInputProps, FieldProps } from 'formik'

export type ProfileFormModel = {
    name: string
    email: string
    title: string
    avatar: string | File
    timeZone: string
    lang: string
    syncData: boolean
}

type ProfileProps = {
    data?: ProfileFormModel
}

type LanguageOption = {
    value: string
    label: string
    imgPath: string
}

const { Control } = components

const validationSchema = Yup.object().shape({
    name: Yup.string()
        .min(3, 'Too Short!')
        .max(12, 'Too Long!')
        .required('User Name Required'),
    email: Yup.string().email('Invalid email').required('Email Required'),
    title: Yup.string(),
    avatar: Yup.string(),
    lang: Yup.string(),
    timeZone: Yup.string(),
    syncData: Yup.bool(),
})

const CustomSelectOption = ({
    innerProps,
    label,
    data,
    isSelected,
}: OptionProps<LanguageOption>) => {
    return (
        <div
            className={`flex items-center justify-between p-2 ${isSelected
                ? 'bg-gray-100 dark:bg-gray-500'
                : 'hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
            {...innerProps}
        >
            <div className="flex items-center">
                <Avatar shape="circle" size={20} src={data.imgPath} />
                <span className="ml-2 rtl:mr-2">{label}</span>
            </div>
            {isSelected && <HiCheck className="text-emerald-500 text-xl" />}
        </div>
    )
}

const CustomControl = ({
    children,
    ...props
}: ControlProps<LanguageOption>) => {
    const selected = props.getValue()[0]
    return (
        <Control {...props}>
            {selected && (
                <Avatar
                    className="ltr:ml-4 rtl:mr-4"
                    shape="circle"
                    size={18}
                    src={selected.imgPath}
                />
            )}
            {children}
        </Control>
    )
}

const langOptions: LanguageOption[] = [
    { value: 'en', label: 'English', imgPath: '/img/countries/us.png' },
    { value: 'fr', label: 'French', imgPath: '/img/countries/fr.png' },
    { value: 'de', label: 'German', imgPath: '/img/countries/de.png' },
]

const Profile = ({
    data = {
        name: '',
        email: '',
        title: '',
        avatar: '',
        timeZone: '',
        lang: '',
        syncData: false,
    },
}: ProfileProps) => {
    const dispatch = useAppDispatch()
    const { authority } = useAppSelector((state) => state.auth.user)

    const onSetFormFile = (
        form: FormikProps<ProfileFormModel>,
        field: FieldInputProps<ProfileFormModel>,
        file: File[]
    ) => {
        form.setFieldValue(field.name, file[0])
    }

    const onFormSubmit = async (
        values: ProfileFormModel,
        setSubmitting: (isSubmitting: boolean) => void
    ) => {
        console.log('values', values)

        const formData = new FormData()
        Object.entries(values).forEach(([key, value]) => {
            if (key === 'avatar') {
                if (value instanceof File) {
                    formData.append(key, value)
                }
            } else {
                formData.append(key, value as string)
            }
        })

        try {
            const response = await apiUpdateAccountSettingData<any, any>(formData)
            if (response.data) {
                const { profile } = response.data
                dispatch(setUser({
                    avatar: profile.avatar,
                    userName: profile.name,
                    email: profile.email,
                    authority: authority
                }))
            }
            toast.push(<Notification title={'Profile updated'} type="success" />, {
                placement: 'top-center',
            })
        } catch (err) {
            console.error('Update profile error:', err)
            toast.push(<Notification title={'Failed to update profile'} type="danger" />, {
                placement: 'top-center',
            })
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <Formik
            enableReinitialize
            initialValues={data}
            validationSchema={validationSchema}
            onSubmit={(values, { setSubmitting }) => {
                setSubmitting(true)
                setTimeout(() => {
                    onFormSubmit(values, setSubmitting)
                }, 1000)
            }}
        >
            {({ values, touched, errors, isSubmitting, resetForm }) => {
                const validatorProps = { touched, errors }
                return (
                    <Form>
                        <FormContainer>
                            <FormDesription
                                title="General"
                                desc="Basic info, like your name and address that will displayed in public"
                            />
                            <FormRow
                                name="name"
                                label="Name"
                                {...validatorProps}
                            >
                                <Field
                                    type="text"
                                    autoComplete="off"
                                    name="name"
                                    placeholder="Name"
                                    component={Input}
                                    prefix={
                                        <HiOutlineUserCircle className="text-xl" />
                                    }
                                />
                            </FormRow>
                            <FormRow
                                name="email"
                                label="Email"
                                {...validatorProps}
                            >
                                <Field
                                    type="email"
                                    autoComplete="off"
                                    name="email"
                                    placeholder="Email"
                                    component={Input}
                                    prefix={
                                        <HiOutlineMail className="text-xl" />
                                    }
                                />
                            </FormRow>
                            <FormRow
                                name="avatar"
                                label="Avatar"
                                {...validatorProps}
                            >
                                <Field name="avatar">
                                    {({ field, form }: FieldProps) => {
                                        const avatarProps = field.value
                                            ? { src: typeof field.value === 'string' ? field.value : URL.createObjectURL(field.value) }
                                            : {}
                                        return (
                                            <Upload
                                                className="cursor-pointer"
                                                showList={false}
                                                uploadLimit={1}
                                                onChange={(files) =>
                                                    onSetFormFile(
                                                        form,
                                                        field,
                                                        files
                                                    )
                                                }
                                                onFileRemove={(files) =>
                                                    onSetFormFile(
                                                        form,
                                                        field,
                                                        files
                                                    )
                                                }
                                            >
                                                <Avatar
                                                    className="border-2 border-white dark:border-gray-800 shadow-lg"
                                                    size={60}
                                                    shape="circle"
                                                    icon={<HiOutlineUser />}
                                                    {...avatarProps}
                                                />
                                            </Upload>
                                        )
                                    }}
                                </Field>
                            </FormRow>
                            <FormRow
                                name="title"
                                label="Title"
                                {...validatorProps}
                                border={false}
                            >
                                <Field
                                    type="text"
                                    autoComplete="off"
                                    name="title"
                                    placeholder="Title"
                                    component={Input}
                                    prefix={
                                        <HiOutlineBriefcase className="text-xl" />
                                    }
                                />
                            </FormRow>
                            <FormDesription
                                className="mt-8"
                                title="Preferences"
                                desc="Your personalized preference displayed in your account"
                            />
                            <FormRow
                                name="lang"
                                label="Language"
                                {...validatorProps}
                            >
                                <Field name="lang">
                                    {({ field, form }: FieldProps) => (
                                        <Select<LanguageOption>
                                            field={field}
                                            form={form}
                                            options={langOptions}
                                            components={{
                                                Option: CustomSelectOption,
                                                Control: CustomControl,
                                            }}
                                            value={langOptions.filter(
                                                (option) =>
                                                    option.value ===
                                                    values?.lang
                                            )}
                                            onChange={(option) =>
                                                form.setFieldValue(
                                                    field.name,
                                                    option?.value
                                                )
                                            }
                                        />
                                    )}
                                </Field>
                            </FormRow>
                            <FormRow
                                name="timeZone"
                                label="Time Zone"
                                {...validatorProps}
                            >
                                <Field
                                    type="text"
                                    autoComplete="off"
                                    name="timeZone"
                                    placeholder="Time Zone"
                                    component={Input}
                                    prefix={
                                        <HiOutlineGlobeAlt className="text-xl" />
                                    }
                                />
                            </FormRow>
                            <FormRow
                                name="syncData"
                                label="Sync Data"
                                {...validatorProps}
                                border={false}
                            >
                                <Field name="syncData" component={Switcher} />
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
                                    {isSubmitting ? 'Updating' : 'Update'}
                                </Button>
                            </div>
                        </FormContainer>
                    </Form>
                )
            }}
        </Formik>
    )
}

export default Profile
