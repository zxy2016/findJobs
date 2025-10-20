import React, { useState } from 'react';
import { Upload, Button, message, Spin, Alert, Card, Descriptions } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios'; // Using axios directly for simplicity in multipart/form-data

const ProfileAnalysis = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysisResult, setAnalysisResult] = useState(null);

    const handleUpload = async (options) => {
        const { file } = options;
        setLoading(true);
        setError(null);
        setAnalysisResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Assuming backend is running on port 8000
            const response = await axios.post('http://localhost:8000/api/v1/profile/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setAnalysisResult(response.data);
            message.success(`${file.name} 上传并分析成功！`);
        } catch (err) {
            const errorMsg = err.response?.data?.detail || '上传或分析失败，请检查文件或联系管理员。';
            setError(errorMsg);
            message.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>个人分析</h1>
            <p>上传您的简历（PDF或DOCX格式），系统将使用LLM分析并提取关键信息。</p>
            
            <Upload
                customRequest={handleUpload}
                maxCount={1}
                showUploadList={false}
                accept=".pdf,.docx"
            >
                <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>

            {loading && <div style={{ marginTop: 24, textAlign: 'center' }}><Spin size="large" /></div>}
            
            {error && <Alert message={error} type="error" style={{ marginTop: 24 }} showIcon />}

            {analysisResult && (
                <Card title="分析结果" style={{ marginTop: 24 }}>
                    <Descriptions bordered column={1} size="small">
                        <Descriptions.Item label="原始文本 (摘要)">
                            {analysisResult.raw_content.substring(0, 500)}...
                        </Descriptions.Item>
                        <Descriptions.Item label="结构化信息 (JSON)">
                            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                                {JSON.stringify(analysisResult.structured_profile, null, 2)}
                            </pre>
                        </Descriptions.Item>
                    </Descriptions>
                </Card>
            )}
        </div>
    );
};

export default ProfileAnalysis;
