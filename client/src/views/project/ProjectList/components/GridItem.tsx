import Card from '@/components/ui/Card'
import ItemDropdown from './ItemDropdown'
import Members from './Members'
import ProgressionBar from './ProgressionBar'
import { HiOutlineClipboardCheck } from 'react-icons/hi'
import { Link } from 'react-router-dom'

export type GridItemProps = {
    data: {
        id: number
        name: string
        category: string
        desc: string
        attachmentCount: number
        totalTask: number
        completedTask: number
        progression: number
        dayleft: number
        status: string
        member: {
            name: string
            img: string
        }[]
    }
}

export type JobItemProps = {
    job: {
        id: number;
        title: string;
        description: string;
        status: string;
        jobtype: string;
        jobtime: string;
        required_skills: string; 
        domain: string;
    };
    onJobUpdated?: () => void;
}

const pay = "$120,000 - $150,000"

const top3Skills = ["5+ years React Experience", "TypeScript", "NextJS"]

const GridItem = ({ job, onJobUpdated }: JobItemProps) => {
    // const { name, totalTask, completedTask, progression, desc, member } = data
    const skills = job.required_skills ? job.required_skills.split(',').map(s => s.trim()) : [];

    return (
        <Card bodyClass="h-full">
            <div className="flex flex-col justify-between h-full">
                <div className="flex justify-between">
                    <Link to={`/app/job?id=${job.id}`}>
                        <h6>{job.title}</h6>
                    </Link>
                    <ItemDropdown job={job} onJobUpdated={onJobUpdated} />
                </div>
                
                <p className="mt-4">{pay}</p>
                <div className="mt-3">
                    {/* <ProgressionBar progression={progression} /> */}
                    <div className="flex items-center justify-between mt-2">
                        {/* <Members members={member} /> */}
                        <div className="flex items-center rounded-full font-semibold text-xs gap-1">
                        {skills.map((skill) => (   
                            <div className="flex items-center px-2 py-1 border border-gray-300 rounded-full">
                                {/* <HiOutlineClipboardCheck className="text-base" /> */}
                                 
                                    <span className="ml-1 rtl:mr-1 whitespace-nowrap">
                                        {skill}
                                    </span>
                                
                            </div>
                        ))}
                        </div>
                    </div>
                </div>
            </div>
        </Card>
    )
}

export default GridItem
