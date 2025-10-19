import axiosInstance from './axiosInstance';

export const getJobs = (params) => {
    return axiosInstance.get('/jobs', { params });
};

export const getLocations = () => {
    return axiosInstance.get('/jobs/locations');
};

export const getCategories = () => {
    return axiosInstance.get('/jobs/categories');
};