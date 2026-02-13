const BASE_URL = 'http://localhost:8000/applicants/';

export async function listApplicants(jobId?: string | number) {
	const url = jobId ? `${BASE_URL}?job=${jobId}` : BASE_URL;
	const res = await fetch(url, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch applicants');
	return res.json();
}

export async function getApplicant(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, { credentials: 'include' });
	if (!res.ok) throw new Error('Failed to fetch applicant');
	return res.json();
}

export async function createApplicant(applicantData: {
	name: string;
	email: string;
	telephone?: string;
	prior_experience?: string;
	source?: string;
	skill_set?: string;
	status?: string;
}) {
	const formData = new FormData();
	formData.append('name', applicantData.name);
	formData.append('email', applicantData.email);
	if (applicantData.telephone) {
		formData.append('telephone', applicantData.telephone);
	}
	if (applicantData.prior_experience) {
		formData.append('prior_experience', applicantData.prior_experience);
	}
	if (applicantData.source) {
		formData.append('source', applicantData.source);
	}
	if (applicantData.skill_set) {
		formData.append('skill_set', applicantData.skill_set);
	}
	if (applicantData.status) {
		formData.append('status', applicantData.status);
	}

	const res = await fetch(BASE_URL, {
		method: 'POST',
		credentials: 'include',
		body: formData,
	});
	
	if (!res.ok) {
		const errorData = await res.json().catch(() => ({ error: 'Failed to create applicant' }));
		throw new Error(errorData.error || errorData.message || 'Failed to create applicant');
	}
	
	return res.json();
}

export async function updateApplicant(id: string | number, applicantData: {
	name?: string;
	email?: string;
	telephone?: string;
	prior_experience?: string;
	source?: string;
	skill_set?: string;
	status?: string;
}) {
	const formData = new FormData();
	if (applicantData.name !== undefined) {
		formData.append('name', applicantData.name);
	}
	if (applicantData.email !== undefined) {
		formData.append('email', applicantData.email);
	}
	if (applicantData.telephone !== undefined) {
		formData.append('telephone', applicantData.telephone);
	}
	if (applicantData.prior_experience !== undefined) {
		formData.append('prior_experience', applicantData.prior_experience);
	}
	if (applicantData.source !== undefined) {
		formData.append('source', applicantData.source);
	}
	if (applicantData.skill_set !== undefined) {
		formData.append('skill_set', applicantData.skill_set);
	}
	if (applicantData.status !== undefined) {
		formData.append('status', applicantData.status);
	}

	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'PUT',
		credentials: 'include',
		body: formData,
	});
	if (!res.ok) throw new Error('Failed to update applicant');
	return res.json();
}

export async function deleteApplicant(id: string | number) {
	const res = await fetch(`${BASE_URL}${id}/`, {
		method: 'DELETE',
		credentials: 'include',
	});
	if (!res.ok) throw new Error('Failed to delete applicant');
	return true;
}
