import pytest
from unittest.mock import MagicMock, patch
from app.services.matching_service import MatchingService
from app.models import UserProfile, Job
from app.schemas.job_match import JobMatchCreate

@pytest.fixture
def db_session_mock():
    return MagicMock()

@pytest.fixture
def matching_service(db_session_mock):
    return MatchingService(db_session_mock)

@patch('app.crud.crud_job_match.create')
@patch('app.services.matching_service.get_llm_client')
@patch('app.crud.crud_job.get_multi')
@patch('app.crud.crud_user_profile.get')
def test_run_matching_for_profile(
    crud_profile_get_mock,
    crud_job_get_multi_mock,
    llm_client_mock,
    crud_job_match_create_mock,
    matching_service,
    db_session_mock
):
    # Arrange
    profile_id = 1
    mock_profile = UserProfile(id=profile_id, structured_profile={'skills': ['Python', 'FastAPI']})
    mock_jobs = [
        Job(id=101, title='Python Developer', description='...'),
        Job(id=102, title='Frontend Engineer', description='...')
    ]
    
    crud_profile_get_mock.return_value = mock_profile
    crud_job_get_multi_mock.return_value = {"items": mock_jobs, "total": len(mock_jobs)} # crud_job.get_multi 返回一个字典
    
    mock_llm_instance = MagicMock()
    llm_client_mock.return_value = mock_llm_instance
    
    # 模拟LLM的返回值
    llm_responses = [
        '{"score": 9, "summary": "Excellent match."}',
        '{"score": 3, "summary": "Not a good fit."}'
    ]
    mock_llm_instance.generate.side_effect = llm_responses

    # Act
    matching_service.run_matching_for_profile(profile_id)

    # Assert
    crud_profile_get_mock.assert_called_once_with(db_session_mock, id=profile_id)
    crud_job_get_multi_mock.assert_called_once_with(db_session_mock)
    
    # 验证LLM被调用了两次 (每个job一次)
    assert mock_llm_instance.generate.call_count == 2
    
    # 验证保存方法被调用了两次
    assert crud_job_match_create_mock.call_count == 2

    # 验证第一次保存的数据是否正确
    first_call_args = crud_job_match_create_mock.call_args_list[0][1]['obj_in']
    assert isinstance(first_call_args, JobMatchCreate)
    assert first_call_args.user_profile_id == profile_id
    assert first_call_args.job_id == 101
    assert first_call_args.match_score == 9
    assert first_call_args.match_summary == "Excellent match."
