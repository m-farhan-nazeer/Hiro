const BASE_URL = 'http://localhost:8000/api/applications/';

// export async function createApplication(formData: FormData) {
//     const res = await fetch(BASE_URL, {
//         method: 'POST',
//         // Let the browser set the Content-Type for FormData (multipart/form-data)
//         body: formData,
//         // credentials may be required depending on backend auth setup
//         // credentials: 'include',
//     });

//     if (!res.ok) {
//         const text = await res.text();
//         throw new Error(`Failed to create application: ${res.status} ${text}`);
//     }

//     return res.json();
// }

export default { createApplication };
// const BASE_URL = 'http://127.0.0.1:8000/api/applications/';

export async function listApplications(jobId?: string | number, status?: string) {
	const params = new URLSearchParams();
	if (jobId) {
		params.append('job', jobId.toString());
	}
	if (status && status !== '') {
		params.append('status', status);
	}
	const url = params.toString() ? `${BASE_URL}?${params.toString()}` : BASE_URL;
	const res = await fetch(url, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch applications');
	return res.json();
}

export async function createApplication(applicationData: {
	name: string;
	email: string;
	job: number; // job_id
	resume_file: File;
	score?: string;
	status?: string;
}) {
	const formData = new FormData();
	formData.append('name', applicationData.name);
	formData.append('email', applicationData.email);
	formData.append('job', applicationData.job.toString());
	formData.append('resume_file', applicationData.resume_file);
	
	// Optional fields with defaults
	if (applicationData.score !== undefined) {
		formData.append('score', applicationData.score);
	}
	if (applicationData.status) {
		formData.append('status', applicationData.status);
	}

	const res = await fetch(BASE_URL, {
		method: 'POST',
		credentials: 'include',
		body: formData,
	});
	
	if (!res.ok) {
		const errorData = await res.json().catch(() => ({ error: 'Failed to create application' }));
		throw new Error(errorData.error || errorData.message || 'Failed to create application');
	}
	
	return res.json();
}

export async function getApplication(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch application');
	return res.json();
}

export async function updateApplication(id: string | number, applicationData: {
	applicant?: number;
	job?: number;
	score?: string;
	status?: string;
	resume_file?: File;
}) {
	const formData = new FormData();
	if (applicationData.applicant !== undefined) {
		formData.append('applicant', applicationData.applicant.toString());
	}
	if (applicationData.job !== undefined) {
		formData.append('job', applicationData.job.toString());
	}
	if (applicationData.score !== undefined) {
		formData.append('score', applicationData.score);
	}
	if (applicationData.status !== undefined) {
		formData.append('status', applicationData.status);
	}
	if (applicationData.resume_file) {
		formData.append('resume_file', applicationData.resume_file);
	}

	// Use PATCH for partial updates (only status), PUT for full updates
	const isStatusOnly = applicationData.status !== undefined && 
		Object.keys(applicationData).filter(key => applicationData[key as keyof typeof applicationData] !== undefined).length === 1;
	const method = isStatusOnly ? 'PATCH' : 'PUT';
	
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: method,
		credentials: 'include',
		body: formData,
	});
	if (!res.ok) {
		const errorData = await res.json().catch(() => ({ error: 'Failed to update application' }));
		throw new Error(errorData.error || errorData.message || 'Failed to update application');
	}
	return res.json();
}

export async function deleteApplication(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'DELETE',
		credentials: 'include',
	});
	if (!res.ok) throw new Error('Failed to delete application');
	return true;
}
