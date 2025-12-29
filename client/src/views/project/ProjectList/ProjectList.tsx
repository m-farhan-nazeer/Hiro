import { useState } from 'react'
import ActionBar from './components/ActionBar'
import ProjectListContent from './components/ProjectListContent'
import NewProjectDialog from './components/NewProjectDialog'
import Container from '@/components/shared/Container'
import reducer from './store'
import { injectReducer } from '@/store'

injectReducer('projectList', reducer)

const ProjectList = () => {
    const [refreshTrigger, setRefreshTrigger] = useState(0)

    const handleJobUpdated = () => {
        // Force refresh by updating a trigger state
        setRefreshTrigger(prev => prev + 1)
    }

    return (
        <Container className="h-full">
            <ActionBar />
            <ProjectListContent refreshTrigger={refreshTrigger} onJobUpdated={handleJobUpdated} />
            <NewProjectDialog onJobUpdated={handleJobUpdated} />
        </Container>
    )
}

export default ProjectList

