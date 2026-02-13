import { useState, useEffect } from 'react'
import Dialog from '@/components/ui/Dialog'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Spinner from '@/components/ui/Spinner'
import { HiRefresh, HiX, HiChevronDown, HiChevronRight, HiExternalLink } from 'react-icons/hi'
import { FaGithub, FaLinkedin, FaBriefcase, FaUserFriends, FaGlobe } from 'react-icons/fa'
import { MdRecommend } from 'react-icons/md'
import ApiService from '@/services/ApiService'
import classNames from 'classnames'

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
    github_url?: string | null
    linkedin_url?: string | null
    linkedin_scrape_status?: 'idle' | 'processing' | 'completed' | 'failed'
    social_insights?: Record<string, any>
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
    const [socialLoading, setSocialLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [skillsExpanded, setSkillsExpanded] = useState(false)
    const [activeTab, setActiveTab] = useState<'resume' | 'social'>('resume')

    const fetchProfile = async (options?: { silent?: boolean }) => {
        if (!applicantId) return

        if (!options?.silent) {
            setLoading(true)
        }
        setError(null)

        try {
            const response = await ApiService.fetchData({
                url: `/applicants/${applicantId}/profile/`,
                method: 'get'
            })
            setProfile(response.data as ApplicantProfile)
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to load profile')
            console.error('Profile fetch error:', err)
        } finally {
            if (!options?.silent) {
                setLoading(false)
            }
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
            setProfile(response.data as ApplicantProfile)
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to refresh profile')
            console.error('Profile refresh error:', err)
        } finally {
            setLoading(false)
        }
    }

    const fetchSocialData = async () => {
        if (!applicantId) return

        setSocialLoading(true)
        setError(null)

        try {
            await ApiService.fetchData({
                url: `/applicants/${applicantId}/social-scrape/`,
                method: 'post'
            })
            // Fetch profile immediately to update status to processing
            fetchProfile({ silent: true })
        } catch (err: any) {
            console.error('Social fetch error:', err)
        } finally {
            setSocialLoading(false)
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

    // Polling for social insights
    useEffect(() => {
        let interval: NodeJS.Timeout

        if (isOpen && applicantId && profile?.linkedin_scrape_status === 'processing') {
            interval = setInterval(() => {
                fetchProfile({ silent: true })
            }, 5000)
        }

        return () => {
            if (interval) clearInterval(interval)
        }
    }, [isOpen, applicantId, profile?.linkedin_scrape_status])

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
                            <div className="flex flex-col gap-1 mt-1">
                                <p className="text-sm text-gray-500">
                                    Extracted from {profile.extraction_source}
                                </p>
                                <div className="flex gap-2 mt-1">
                                    {profile.github_url && (
                                        <a
                                            href={profile.github_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                                            title="GitHub Profile"
                                        >
                                            <FaGithub size={20} />
                                        </a>
                                    )}
                                    {profile.linkedin_url && (
                                        <a
                                            href={profile.linkedin_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-[#0077b5] hover:text-[#006396] transition-colors"
                                            title="LinkedIn Profile"
                                        >
                                            <FaLinkedin size={20} />
                                        </a>
                                    )}
                                </div>
                            </div>
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

                {/* Tabs */}
                {profile && (
                    <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                        <button
                            className={classNames(
                                'px-4 py-2 font-medium text-sm transition-colors border-b-2',
                                activeTab === 'resume'
                                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                            )}
                            onClick={() => setActiveTab('resume')}
                        >
                            Resume Insights
                        </button>
                        <button
                            className={classNames(
                                'px-4 py-2 font-medium text-sm transition-colors border-b-2',
                                activeTab === 'social'
                                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                            )}
                            onClick={() => setActiveTab('social')}
                        >
                            Social Insights
                        </button>
                    </div>
                )}

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

                {!loading && profile && activeTab === 'resume' && (
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

                {!loading && profile && activeTab === 'social' && (
                    <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2">
                        {!profile.linkedin_url ? (
                            <div className="text-center py-8 text-gray-500">
                                <p>No LinkedIn URL found in resume.</p>
                            </div>
                        ) : (
                            <div>
                                {!profile.social_insights || Object.keys(profile.social_insights).length === 0 || profile.linkedin_scrape_status === 'processing' ? (
                                    <div className="text-center py-8">
                                        {profile.linkedin_scrape_status === 'processing' ? (
                                            <div className="flex flex-col items-center">
                                                <Spinner size={30} className="mb-4" />
                                                <p className="text-blue-600 dark:text-blue-400 font-medium">
                                                    LinkedIn scraping in progress...
                                                </p>
                                                <p className="text-sm text-gray-400 mt-1">
                                                    This may take up to a minute. Data will appear automatically.
                                                </p>
                                            </div>
                                        ) : (
                                            <>
                                                <p className="text-gray-600 dark:text-gray-400 mb-4">
                                                    Fetch insights from LinkedIn profile to verify skills and experience.
                                                </p>
                                                <Button
                                                    variant="solid"
                                                    loading={socialLoading}
                                                    onClick={fetchSocialData}
                                                    icon={<FaLinkedin />}
                                                >
                                                    Fetch Social Insights
                                                </Button>
                                            </>
                                        )}
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        {/* Profile Header Card */}
                                        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 p-6 rounded-xl border border-blue-100 dark:border-gray-700">
                                            <div className="flex gap-4">
                                                {profile.social_insights.profile_picture ? (
                                                    <img src={profile.social_insights.profile_picture} alt="Profile" className="w-20 h-20 rounded-full border-4 border-white dark:border-gray-700 shadow" />
                                                ) : (
                                                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-2xl font-bold">
                                                        {profile.applicant_name?.charAt(0) || '?'}
                                                    </div>
                                                )}
                                                <div className="flex-1">
                                                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">{profile.applicant_name}</h3>
                                                    <div className="flex flex-wrap gap-3 mb-2">
                                                        {profile.social_insights.location && (
                                                            <span className="text-sm text-gray-600 dark:text-gray-300">📍 {profile.social_insights.location}</span>
                                                        )}
                                                        {profile.social_insights.connections && (
                                                            <span className="px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium">🔗 {profile.social_insights.connections} connections</span>
                                                        )}
                                                    </div>
                                                    {(profile.social_insights.current_position?.title || profile.social_insights.current_position?.company) && (
                                                        <div className="flex gap-2">
                                                            <span className="text-gray-500 dark:text-gray-400">💼</span>
                                                            <div>
                                                                <p className="font-semibold text-gray-900 dark:text-white">
                                                                    {profile.social_insights.current_position.title || 'Position not listed'}
                                                                </p>
                                                                {profile.social_insights.current_position.company && (
                                                                    <p className="text-sm text-gray-600 dark:text-gray-300">{profile.social_insights.current_position.company}</p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                                <FaLinkedin className="text-3xl text-[#0077b5]" />
                                            </div>
                                        </div>

                                        {/* Headline */}
                                        {profile.social_insights.headline && (
                                            <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700">
                                                <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">Professional Headline</h4>
                                                <p className="text-gray-900 dark:text-gray-100">{profile.social_insights.headline}</p>
                                            </div>
                                        )}

                                        {/* About */}
                                        {profile.social_insights.about && (
                                            <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700">
                                                <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">About</h4>
                                                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{profile.social_insights.about}</p>
                                            </div>
                                        )}

                                        {/* Work Experience Timeline */}
                                        {profile.social_insights.experiences && profile.social_insights.experiences.length > 0 && (
                                            <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700">
                                                <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-4 flex items-center gap-2">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                                    </svg>
                                                    Work Experience ({profile.social_insights.experiences.length})
                                                </h4>
                                                <div className="space-y-4">
                                                    {profile.social_insights.experiences.map((exp: any, idx: number) => (
                                                        <div key={idx} className="flex gap-3 pb-4 border-b border-gray-100 dark:border-gray-700 last:border-0 last:pb-0">
                                                            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-semibold">
                                                                {idx + 1}
                                                            </div>
                                                            <div className="flex-1">
                                                                <h5 className="font-semibold text-gray-900 dark:text-white">
                                                                    {exp.title || 'Position not listed'}
                                                                </h5>
                                                                {exp.company && (
                                                                    <p className="text-gray-700 dark:text-gray-300 text-sm mt-0.5">
                                                                        {exp.company}
                                                                    </p>
                                                                )}
                                                                {exp.duration && (
                                                                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                                                                        {exp.duration}
                                                                    </p>
                                                                )}
                                                                {exp.location && (
                                                                    <p className="text-gray-500 dark:text-gray-400 text-xs mt-0.5">
                                                                        📍 {exp.location}
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Error */}
                                        {profile.social_insights.error && (
                                            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                                                <p className="text-red-700 dark:text-red-300 text-sm"><strong>Note:</strong> {profile.social_insights.error}</p>
                                            </div>
                                        )}

                                        <div className="flex justify-center">
                                            <Button size="sm" variant="plain" loading={socialLoading} onClick={fetchSocialData} icon={<HiRefresh />}>Refresh Data</Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
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
