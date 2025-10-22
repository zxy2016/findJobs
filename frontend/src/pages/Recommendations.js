import React, { useState, useEffect } from 'react';
import { Button, List, Card, Progress, Typography, message, Spin, Empty, Space, Radio } from 'antd';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

// 创建一个自定义的 axios 实例，用于后续的 API 调用
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
});

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [sortOrder, setSortOrder] = useState('desc'); // 'desc' or 'asc'

  // 处理排序变化的函数
  const handleSortChange = (e) => {
    const newSortOrder = e.target.value;
    setSortOrder(newSortOrder);
    const sortedData = [...recommendations].sort((a, b) => {
      return newSortOrder === 'desc' ? b.match_score - a.match_score : a.match_score - b.match_score;
    });
    setRecommendations(sortedData);
  };

  // 获取推荐数据的函数
  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/profiles/1/recommendations');
      // 按匹配度降序排序
      const sortedData = response.data.sort((a, b) => b.match_score - a.match_score);
      setRecommendations(sortedData);
    } catch (error) {
      message.error('获取推荐数据失败，请稍后再试。');
      console.error('Fetch recommendations error:', error);
    }
    setLoading(false);
  };

  // 触发匹配任务的函数
  const handleTriggerMatching = async () => {
    setMatching(true);
    try {
      await apiClient.post('/profiles/1/match');
      message.success('智能匹配任务已成功触发！结果将在几分钟后更新。');
    } catch (error) {
      if (error.response && error.response.status === 404) {
        message.error('触发匹配失败：找不到用户画像。请先在“个人分析”页面上传简历。');
      } else {
        message.error('触发匹配任务失败，请检查后端服务是否正常。');
      }
      console.error('Trigger matching error:', error);
    }
    setMatching(false);
  };

  // 组件加载时自动获取一次数据
  useEffect(() => {
    fetchRecommendations();
  }, []);

  return (
    <Card>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Title level={3}>智能岗位推荐</Title>
        <Paragraph>
          这里将基于您最新上传的简历，为您智能匹配最合适的岗位。匹配过程可能需要几分钟，请耐心等待。
        </Paragraph>
        <Space>
            <Button 
                type="primary" 
                onClick={handleTriggerMatching} 
                loading={matching}
            >
                开始智能匹配
            </Button>
            <Button onClick={fetchRecommendations} loading={loading}>
                刷新推荐结果
            </Button>
        </Space>

        <Radio.Group onChange={handleSortChange} value={sortOrder}>
          <Radio.Button value="desc">按匹配度降序</Radio.Button>
          <Radio.Button value="asc">按匹配度升序</Radio.Button>
        </Radio.Group>

        <Spin spinning={loading} tip="正在加载推荐结果...">
          {recommendations.length > 0 ? (
            <List
              grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
              dataSource={recommendations}
              renderItem={(item) => {
                // 添加防御性检查，如果 job 数据不存在则不渲染该卡片
                if (!item.job) {
                  return null;
                }
                return (
                  <List.Item>
                    <Card 
                      title={item.job.title}
                      hoverable
                      extra={<a href={item.job.url} target="_blank" rel="noopener noreferrer">查看原链接</a>}
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                          <Text strong>{item.job.company}</Text>
                          <Text type="secondary">{item.job.location}</Text>
                          <Space align="center">
                              <Text strong style={{ fontSize: '16px' }}>匹配度:</Text>
                              <Progress 
                                  type="circle" 
                                  percent={item.match_score * 10} 
                                  width={60} 
                                  format={(percent) => `${percent / 10}`}
                              />
                          </Space>
                          <Paragraph ellipsis={{ rows: 4, expandable: true, symbol: '更多' }}>
                              <strong>AI推荐理由:</strong> {item.match_summary}
                          </Paragraph>
                          {item.improvement_suggestions && (
                            <Paragraph type="secondary" ellipsis={{ rows: 3, expandable: true, symbol: '更多' }}>
                                <strong>提升建议:</strong> {item.improvement_suggestions}
                            </Paragraph>
                          )}
                      </Space>
                    </Card>
                  </List.Item>
                );
              }}
            />
          ) : (
            !loading && <Empty description="暂无推荐结果，请先点击“开始智能匹配”按钮。" />
          )}
        </Spin>
      </Space>
    </Card>
  );
};

export default Recommendations;