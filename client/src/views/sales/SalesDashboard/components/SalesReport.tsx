import Card from '@/components/ui/Card'
import Chart from '@/components/shared/Chart'

type SalesReportProps = {
    data?: {
        series?: {
            name: string
            data: number[]
        }[]
        categories?: string[]
    }
    className?: string
}

const SalesReport = ({ className, data = {} }: SalesReportProps) => {
    const mutableSeries = data.series?.map(s => ({ ...s })) || []
    const mutableCategories = data.categories ? [...data.categories] : []

    return (
        <Card className={className}>
            <div className="flex items-center justify-between">
                <h4>Recruitment Report</h4>
            </div>
            <Chart
                series={mutableSeries}
                xAxis={mutableCategories}
                height="380px"
                customOptions={{ legend: { show: false } }}
            />
        </Card>
    )
}


export default SalesReport
