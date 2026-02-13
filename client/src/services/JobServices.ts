const BASE_URL = 'http://localhost:8000/api/jobs/';

export async function listJobs() {
	const res = await fetch(BASE_URL, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch jobs');
	return res.json();
}

export async function createJob(jobData: {
	title: string;
	description: string;
	status: string;
	jobtype: string;
	jobtime: string;
	required_skills: string;
	domain: string;
}) {
	const res = await fetch(BASE_URL, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include',
		body: JSON.stringify(jobData),
	});
	if (!res.ok) throw new Error('Failed to create job');
	return res.json();
}

export async function getJob(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch job');
	return res.json();
}

export async function updateJob(id: string | number, jobData: {
	title: string;
	description: string;
	status: string;
	jobtype: string;
	jobtime: string;
	required_skills: string;
	domain: string;
}) {
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include',
		body: JSON.stringify(jobData),
	});
	if (!res.ok) throw new Error('Failed to update job');
	return res.json();
}

export async function patchJob(id: string | number, patchData: Partial<{
	title: string;
	description: string;
	status: string;
	jobtype: string;
	jobtime: string;
	required_skills: string;
	domain: string;
}>) {
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include',
		body: JSON.stringify(patchData),
	});
	if (!res.ok) throw new Error('Failed to patch job');
	return res.json();
}

export async function deleteJob(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'DELETE',
		credentials: 'include',
	});
	if (!res.ok) throw new Error('Failed to delete job');
	return true;
}

	
