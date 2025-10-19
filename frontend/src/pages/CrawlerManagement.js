import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Row, Col, App, Tag } from 'antd';
import { PartitionOutlined, SyncOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { triggerScrapeTask, getScrapeStatus } from '../api/crawlerApi';

const crawlerList = [
    {
        key: 'haier',
        name: '海尔招聘',
        description: '爬取海尔官网的职位，支持增量更新。'
    },
];

const StatusTag = ({ status }) => {
    const statusMap = {
        running: <Tag icon={<SyncOutlined spin />} color="processing">运行中</Tag>,
        success: <Tag icon={<CheckCircleOutlined />} color="success">执行成功</Tag>,
        failed: <Tag icon={<CloseCircleOutlined />} color="error">执行失败</Tag>,
        idle: <Tag color="default">空闲</Tag>,
    };
    return statusMap[status] || statusMap.idle;
};

const CrawlerManagement = () => {
    const { message } = App.useApp();
    const [statuses, setStatuses] = useState({});
    const intervalRef = useRef(null);

    // 移除 useCallback，确保函数在每次渲染时都是最新的
    const fetchAllStatuses = async () => {
        console.log("Fetching all statuses...");
        const promises = crawlerList.map(c => getScrapeStatus(c.key));
        try {
            const results = await Promise.all(promises);
            const newStatuses = {};
            let isAnyTaskRunning = false;
            results.forEach(res => {
                newStatuses[res.data.site_name] = res.data.status;
                if (res.data.status === 'running') {
                    isAnyTaskRunning = true;
                }
            });
            setStatuses(newStatuses);

            if (!isAnyTaskRunning && intervalRef.current) {
                console.log("No tasks running, stopping poll.");
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        } catch (error) {
            console.error("获取状态失败:", error);
        }
    };

    useEffect(() => {
        fetchAllStatuses(); // 组件加载时获取一次初始状态

        // 组件卸载时，确保清除定时器
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []); // 空依赖数组确保这个 effect 只在挂载和卸载时运行一次

    const handleScrape = async (siteName) => {
        try {
            const response = await triggerScrapeTask(siteName);
            message.success(response.data.message || '任务已成功提交！');
            setStatuses(prev => ({ ...prev, [siteName]: 'running' }));

            // 如果当前没有定时器在运行，则启动一个新的
            if (!intervalRef.current) {
                console.log("Task started, beginning to poll.");
                intervalRef.current = setInterval(fetchAllStatuses, 3000);
            }
        } catch (error) {
            message.error(error.response?.data?.detail || '提交任务失败。');
        }
    };

    return (
        <div>
            <h1>爬虫管理</h1>
            <p>管理并手动触发系统中的爬虫任务。</p>
            <Row gutter={[16, 16]}>
                {crawlerList.map(crawler => {
                    const status = statuses[crawler.key] || 'idle';
                    const isLoading = status === 'running';
                    return (
                        <Col span={8} key={crawler.key}>
                            <Card 
                                title={<span><PartitionOutlined style={{ marginRight: 8 }} />{crawler.name}</span>}
                                extra={<StatusTag status={status} />}
                                bordered={false} 
                                style={{ boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)' }}
                            >
                                <p>{crawler.description}</p>
                                <div style={{ marginTop: '16px', textAlign: 'right' }}>
                                    <Button 
                                        type="primary" 
                                        onClick={() => handleScrape(crawler.key)}
                                        loading={isLoading}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? '正在执行' : '立即执行'}
                                    </Button>
                                </div>
                            </Card>
                        </Col>
                    )
                })}
            </Row>
        </div>
    );
};

export default CrawlerManagement;
