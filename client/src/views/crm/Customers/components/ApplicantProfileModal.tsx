import { useState, useEffect } from 'react'
import Dialog from '@/components/ui/Dialog'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Spinner from '@/components/ui/Spinner'
import { HiRefresh, HiX, HiChevronDown, HiChevronRight } from 'react-icons/hi'
import ApiService from '@/services/ApiService'

interface Skill {
    name: string
    category: string
    proficiency?: string | null
}

interface Experience {
    company: string
    title: string
    duration: string
    description: string
}

interface Education {
    institution: string
    degree: string
    field: string | null
    year: string
}

interface Certification {
    name: string
    issuer: string
    year?: string | null
}

interface ApplicantProfile {
    id: number
    applicant: number
    applicant_name: string
    applicant_email: string
    summary: string
    skills: Skill[]
    experience: Experience[]
    education: Education[]
    certifications: Certification[]
    total_experience_years?: number | null
    extracted_at: string
    extraction_source: string
}

interface ApplicantProfileModalProps {
    applicantId: number | null
    applicantName: string
    isOpen: boolean
    onClose: () => void
}

const ApplicantProfileModal = ({
    applicantId,
    applicantName,
    isOpen,
    onClose
}: ApplicantProfileModalProps) => {
    const [profile, setProfile] = useState<ApplicantProfile | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [skillsExpanded, setSkillsExpanded] = useState(false)

    const fetchProfile = async () => {
        if (!applicantId) return

        setLoading(true)
        setError(null)

        try {
            const response = await ApiService.fetchData({
                url: `/applicants/${applicantId}/profile/`,
                method: 'get'
            })
            setProfile(response.data)
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to load profile')
            console.error('Profile fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const refreshProfile = async () => {
        if (!applicantId) return

        setLoading(true)
        setError(null)

        try {
            const response = await ApiService.fetchData({
                url: `/applicants/${applicantId}/profile/refresh/`,
                method: 'post'
            })
            setProfile(response.data)
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to refresh profile')
            console.error('Profile refresh error:', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (isOpen && applicantId) {
            fetchProfile()
        }
        // Reset state when modal closes
        if (!isOpen) {
            setProfile(null)
            setError(null)
        }
    }, [isOpen, applicantId])

    // Group skills by category
    const skillsByCategory = profile?.skills.reduce((acc, skill) => {
        if (!acc[skill.category]) acc[skill.category] = []
        acc[skill.category].push(skill)
        return acc
    }, {} as Record<string, Skill[]>) || {}

    return (
        <Dialog
            isOpen={isOpen}
            onClose={onClose}
            width={900}
            closable={false}
            overlayClassName="bg-black/80"
        >
            <div className="bg-white dark:bg-gray-900 -m-6 p-6 rounded-lg">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h4 className="text-xl font-bold">{applicantName}'s Profile</h4>
                        {profile && (
                            <p className="text-sm text-gray-500 mt-1">
                                Extracted from {profile.extraction_source}
                            </p>
                        )}
                    </div>
                    <div className="flex gap-2">
                        <Button
                            size="sm"
                            variant="plain"
                            icon={<HiRefresh />}
                            onClick={refreshProfile}
                            disabled={loading}
                            title="Re-extract profile from resume"
                        >
                            Refresh
                        </Button>
                        <Button
                            size="sm"
                            variant="plain"
                            icon={<HiX />}
                            onClick={onClose}
                        />
                    </div>
                </div>

                {loading && (
                    <div className="flex flex-col items-center justify-center py-16">
                        <Spinner size={40} />
                        <p className="text-gray-500 mt-4">
                            {profile ? 'Refreshing profile...' : 'Extracting insights from resume...'}
                        </p>
                        <p className="text-sm text-gray-400 mt-1">This may take 10-30 seconds</p>
                    </div>
                )}

                {error && !loading && (
                    <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded mb-4">
                        <p className="font-semibold">Error</p>
                        <p className="text-sm mt-1">{error}</p>
                    </div>
                )}

                {!loading && profile && (
                    <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2">

                        {/* Skills - Collapsible */}
                        {profile.skills.length > 0 && (
                            <div className="border border-gray-200 dark:border-gray-700 rounded-lg">
                                <button
                                    onClick={() => setSkillsExpanded(!skillsExpanded)}
                                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        {skillsExpanded ? <HiChevronDown className="text-lg" /> : <HiChevronRight className="text-lg" />}
                                        <h5 className="font-semibold flex items-center gap-2">
                                            <span>💡 Skills</span>
                                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                                                {profile.skills.length}
                                            </span>
                                        </h5>
                                    </div>
                                </button>
                                {skillsExpanded && (
                                    <div className="px-4 pb-4 space-y-4 border-t border-gray-200 dark:border-gray-700 pt-4">
                                        {Object.entries(skillsByCategory).map(([category, skills]) => (
                                            <div key={category}>
                                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                                    {category}
                                                </p>
                                                <div className="flex flex-wrap gap-2">
                                                    {skills.map((skill, idx) => (
                                                        <span
                                                            key={idx}
                                                            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                                                        >
                                                            {skill.name}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Experience */}
                        {profile.experience.length > 0 && (
                            <div>
                                <h5 className="font-semibold mb-3 flex items-center gap-2">
                                    <span>💼 Work Experience</span>
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                                        {profile.experience.length}
                                    </span>
                                </h5>
                                <div className="space-y-4">
                                    {profile.experience.map((exp, idx) => (
                                        <div
                                            key={idx}
                                            className="border-l-4 border-blue-500 dark:border-blue-400 pl-4 py-2"
                                        >
                                            <p className="font-semibold text-gray-900 dark:text-gray-100">
                                                {exp.title}
                                            </p>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                                                {exp.company}
                                            </p>
                                            <p className="text-sm text-gray-500 dark:text-gray-500">
                                                {exp.duration}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Education */}
                        {profile.education.length > 0 && (
                            <div>
                                <h5 className="font-semibold mb-3 flex items-center gap-2">
                                    <span>🎓 Education</span>
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                                        {profile.education.length}
                                    </span>
                                </h5>
                                <div className="space-y-3">
                                    {profile.education.map((edu, idx) => (
                                        <div key={idx} className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded">
                                            <p className="font-semibold text-gray-900 dark:text-gray-100">
                                                {edu.degree}{edu.field && ` in ${edu.field}`}
                                            </p>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                                {edu.institution}
                                            </p>
                                            <p className="text-sm text-gray-500 dark:text-gray-500">
                                                {edu.year}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Certifications */}
                        {profile.certifications.length > 0 && (
                            <div>
                                <h5 className="font-semibold mb-3 flex items-center gap-2">
                                    <span>🏆 Certifications</span>
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                                        {profile.certifications.length}
                                    </span>
                                </h5>
                                <div className="space-y-2">
                                    {profile.certifications.map((cert, idx) => (
                                        <div
                                            key={idx}
                                            className="flex justify-between items-start bg-gray-50 dark:bg-gray-800/50 p-3 rounded"
                                        >
                                            <span className="font-medium text-gray-900 dark:text-gray-100">
                                                {cert.name}
                                            </span>
                                            <span className="text-sm text-gray-500 dark:text-gray-400 text-right">
                                                {cert.issuer}
                                                {cert.year && ` • ${cert.year}`}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Footer */}
                        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                            <p className="text-xs text-gray-400 dark:text-gray-500">
                                Extracted on: {new Date(profile.extracted_at).toLocaleString()}
                            </p>
                        </div>
                    </div>
                )}

                {!loading && !profile && !error && (
                    <div className="text-center py-12 text-gray-500">
                        <p>No profile data available</p>
                    </div>
                )}
            </div>
        </Dialog>
    )
}

export default ApplicantProfileModal
