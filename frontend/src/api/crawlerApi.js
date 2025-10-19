import axiosInstance from './axiosInstance';

export const triggerScrapeTask = (siteName) => {
    return axiosInstance.post(`/scrape/${siteName}`);
};

export const getScrapeStatus = (siteName) => {
    return axiosInstance.get(`/scrape/status/${siteName}`);
};
