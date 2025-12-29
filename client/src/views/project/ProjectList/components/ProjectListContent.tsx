import { useEffect } from 'react'
import { listJobs } from '@/services/JobServices'
import classNames from 'classnames'
import GridItem from './GridItem'
import ListItem, { JobListItem } from './ListItem'
import Spinner from '@/components/ui/Spinner'
import { getList, useAppDispatch, useAppSelector } from '../store'

import { useState } from 'react'

type ProjectListContentProps = {
    onJobUpdated?: () => void;
    refreshTrigger?: number; // When this changes, re-fetch jobs
}

const ProjectListContent = ({ onJobUpdated, refreshTrigger = 0 }: ProjectListContentProps) => {
    const [jobs, setJobs] = useState<any[]>([]);

    const fetchJobs = async () => {
        try {
            const result = await listJobs();
            setJobs(result || []);
            console.log(result);
        } catch (error) {
            console.error('Failed to fetch jobs:', error);
        }
    };

    // Fetch jobs on mount and whenever refreshTrigger changes
    useEffect(() => {
        fetchJobs();
    }, [refreshTrigger]);

    const handleJobUpdated = () => {
        fetchJobs(); // Refresh the jobs list
        onJobUpdated?.(); // Also call parent callback if provided
    };
    const dispatch = useAppDispatch()

    const loading = useAppSelector((state) => state.projectList.data.loading)
    const projectList = useAppSelector(
        (state) => state.projectList.data.projectList
    )
    const view = useAppSelector((state) => state.projectList.data.view)
    const { sort, search } = useAppSelector(
        (state) => state.projectList.data.query
    )

    useEffect(() => {
        dispatch(getList({ sort, search }))
    }, [dispatch, sort, search])

    return (
        <div
            className={classNames(
                'mt-6 h-full flex flex-col',
                loading && 'justify-center'
            )}
        >
            {loading && (
                <div className="flex justify-center">
                    <Spinner size={40} />
                </div>
            )}
            {view === 'grid' && jobs.length > 0 && !loading && (
                // <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div className="grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-4">
                    {jobs.map((job) => (
                        <GridItem key={job.id} job={job} onJobUpdated={handleJobUpdated} />
                    ))}
                </div>
            )}
            {view === 'list' && jobs.length > 0 && !loading && (
                <div>
                    {jobs.map((job) => (
                        <JobListItem key={job.id} job={job} onJobUpdated={onJobUpdated} />
                    ))}
                </div>
            )}
            {view === 'list' &&
                projectList.length > 0 &&
                !loading &&
                jobs.length === 0 &&
                projectList.map((project) => (
                    <ListItem key={project.id} data={project} />
                ))}
        </div>
    )
}

export default ProjectListContent
