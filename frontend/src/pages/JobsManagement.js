import React, { useState, useEffect, useCallback } from 'react';
import { Table, Input, Space, Alert, Drawer, Descriptions, Tag, Select, Radio, Form, Row, Col, Button } from 'antd';
import { getJobs, getLocations, getCategories } from '../api/jobsApi';
import ResizableTitle from '../components/ResizableTitle';

const { Search } = Input;

const JobsManagement = () => {
    const [form] = Form.useForm(); // 1. 创建表单实例
    const [jobs, setJobs] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
    const [sorter, setSorter] = useState({});
    const [filters, setFilters] = useState({ keyword: '', location: null, category: null, published_days: null });
    const [locations, setLocations] = useState([]);
    const [categories, setCategories] = useState([]);
    const [columns, setColumns] = useState([
        { title: '职位名称', dataIndex: 'title', key: 'title', sorter: true, width: 200 },
        { title: '部门信息', dataIndex: 'department_info', key: 'department_info', width: 250 },
        { title: '公司', dataIndex: 'company', key: 'company', width: 150 },
        { title: '地点', dataIndex: 'location', key: 'location', sorter: true, width: 150 },
        { title: '薪资', dataIndex: 'salary_info', key: 'salary_info', width: 120 },
        { title: '经验要求', dataIndex: 'experience_required', key: 'experience_required', width: 120 },
        { title: '学历要求', dataIndex: 'education_required', key: 'education_required', width: 120 },
        { title: '发布/更新时间', dataIndex: 'published_at', key: 'published_at', sorter: true, width: 180 },
        { title: '状态', dataIndex: 'is_active', key: 'is_active', render: isActive => (isActive ? <Tag color="green">在线</Tag> : <Tag color="red">下线</Tag>), width: 80 },
    ]);
    const [drawerVisible, setDrawerVisible] = useState(false);
    const [selectedJob, setSelectedJob] = useState(null);

    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const [locs, cats] = await Promise.all([getLocations(), getCategories()]);
                setLocations(locs.data);
                setCategories(cats.data);
            } catch (err) { console.error("获取筛选选项失败", err); }
        };
        fetchOptions();
    }, []);

    const fetchJobsData = useCallback(async (params) => {
        setLoading(true);
        setError(null);
        try {
            const response = await getJobs(params);
            setJobs(response.data.items);
            setTotal(response.data.total);
        } catch (err) { setError('获取岗位数据失败，请稍后重试。'); }
        setLoading(false);
    }, []);

    useEffect(() => {
        const params = { skip: (pagination.current - 1) * pagination.pageSize, limit: pagination.pageSize, sort_by: sorter.field, sort_order: sorter.order === 'ascend' ? 'asc' : 'desc', ...filters };
        fetchJobsData(params);
    }, [pagination, sorter, filters, fetchJobsData]);

    const handleTableChange = (pagination, filters, sorter) => {
        setPagination(pagination);
        setSorter(sorter);
    };

    // 2. 当表单值变化时，更新筛选状态
    const onFormValuesChange = (changedValues, allValues) => {
        setFilters(prev => ({ ...prev, ...changedValues }));
        setPagination(prev => ({ ...prev, current: 1 }));
    };

    const resetFilters = () => {
        form.resetFields(); // 3. 重置表单的显示
        setFilters({ keyword: '', location: null, category: null, published_days: null });
        setPagination(prev => ({ ...prev, current: 1 }));
    };

    const handleResize = index => (e, { size }) => {
        const nextColumns = [...columns];
        nextColumns[index] = { ...nextColumns[index], width: size.width };
        setColumns(nextColumns);
    };

    const showDrawer = (record) => {
        setSelectedJob(record);
        setDrawerVisible(true);
    };

    const resizableColumns = columns.map((col, index) => ({ ...col, onHeaderCell: column => ({ width: column.width, onResize: handleResize(index) }) }));

    return (
        <div>
            <h1>岗位管理</h1>
            <Form form={form} layout="inline" onValuesChange={onFormValuesChange} style={{ marginBottom: 16 }}>
                <Row gutter={[16, 8]} style={{width: '100%'}}>
                    <Col><Form.Item name="keyword"><Search placeholder="搜索关键词..." enterButton /></Form.Item></Col>
                    <Col><Form.Item name="location"><Select placeholder="所有地点" allowClear showSearch style={{ width: 150 }} options={locations.map(l => ({ value: l, label: l }))} filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} /></Form.Item></Col>
                    <Col><Form.Item name="category"><Select placeholder="所有职能" allowClear showSearch style={{ width: 150 }} options={categories.map(c => ({ value: c, label: c }))} filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())} /></Form.Item></Col>
                    <Col><Form.Item name="published_days"><Radio.Group><Radio.Button value={3}>近3天</Radio.Button><Radio.Button value={7}>近7天</Radio.Button><Radio.Button value={30}>近30天</Radio.Button></Radio.Group></Form.Item></Col>
                    <Col><Button onClick={resetFilters}>重置筛选</Button></Col>
                </Row>
            </Form>
            {error && <Alert message={error} type="error" style={{ marginBottom: 16 }} />}
            <Table
                components={{ header: { cell: ResizableTitle } }}
                columns={resizableColumns}
                dataSource={jobs}
                rowKey="id"
                loading={loading}
                pagination={{ ...pagination, total: total, showSizeChanger: true, showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条 / 共 ${total} 条` }}
                onChange={handleTableChange}
                scroll={{ x: 'max-content' }}
                onRow={(record) => ({ onClick: () => showDrawer(record) })}
            />
            <Drawer width={640} placement="right" closable={true} onClose={() => setDrawerVisible(false)} open={drawerVisible} title={selectedJob?.title}>
                {selectedJob && <Descriptions bordered column={1} size="small">{/* ... 详情 ... */}</Descriptions>}
            </Drawer>
        </div>
    );
};

export default JobsManagement;