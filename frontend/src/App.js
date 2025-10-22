import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, App as AntApp } from 'antd';
import { DatabaseOutlined, PartitionOutlined, UserOutlined, AimOutlined } from '@ant-design/icons';

import JobsManagement from './pages/JobsManagement';
import CrawlerManagement from './pages/CrawlerManagement';
import ProfileAnalysis from './pages/ProfileAnalysis';
import Recommendations from './pages/Recommendations';

const { Header, Content, Sider } = Layout;

const App = () => {
    const location = useLocation();

    return (
        <AntApp>
            <Layout style={{ minHeight: '100vh' }}>
                <Sider collapsible>
                    <div style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.2)', color: 'white', textAlign: 'center', lineHeight: '32px', borderRadius: '6px' }}>FindJobs AI</div>
                    <Menu theme="dark" selectedKeys={[location.pathname]} mode="inline">
                        <Menu.Item key="/jobs" icon={<DatabaseOutlined />}>
                            <Link to="/jobs">岗位管理</Link>
                        </Menu.Item>
                        <Menu.Item key="/crawlers" icon={<PartitionOutlined />}>
                            <Link to="/crawlers">爬虫管理</Link>
                        </Menu.Item>
                        <Menu.Item key="/profile" icon={<UserOutlined />}>
                            <Link to="/profile">个人分析</Link>
                        </Menu.Item>
                        <Menu.Item key="/recommendations" icon={<AimOutlined />}>
                            <Link to="/recommendations">岗位推荐</Link>
                        </Menu.Item>
                    </Menu>
                </Sider>
                <Layout className="site-layout">
                    <Header className="site-layout-background" style={{ padding: 0 }} />
                    <Content style={{ margin: '16px' }}>
                        <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
                            <Routes>
                                <Route path="/jobs" element={<JobsManagement />} />
                                <Route path="/crawlers" element={<CrawlerManagement />} />
                                <Route path="/profile" element={<ProfileAnalysis />} />
                                <Route path="/recommendations" element={<Recommendations />} />
                                <Route path="/" element={<JobsManagement />} /> {/* 默认页面为岗位管理 */}
                            </Routes>
                        </div>
                    </Content>
                </Layout>
            </Layout>
        </AntApp>
    );
};

const AppWrapper = () => (
    <Router>
        <App />
    </Router>
);

export default AppWrapper;