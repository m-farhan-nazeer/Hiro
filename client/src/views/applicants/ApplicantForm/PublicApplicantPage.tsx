import ApplicantForm from './ApplicantForm'

/**
 * Public Application Page
 * 
 * This page is accessible without authentication and allows
 * any user to submit a job application via a shared link.
 */
const PublicApplicantPage = () => {
    const handleSubmitted = () => {
        // Optionally redirect or show a success page after submission
        console.log('Application submitted successfully')
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                        Job Application
                    </h2>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        Submit your application to join our team
                    </p>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
                    <ApplicantForm onSubmitted={handleSubmitted} />
                </div>

                <p className="text-center text-xs text-gray-500 dark:text-gray-400">
                    We'll review your application and get back to you soon.
                </p>
            </div>
        </div>
    )
}

export default PublicApplicantPage
