import axios from 'axios';

// 创建一个 Axios 实例
const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1', // 后端 API 的基础 URL
    timeout: 10000, // 请求超时时间
});

export default axiosInstance;
