import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import docx
import pypdf

from app.db.session import get_db
from app.services.llm_client import get_llm_client, LLMClient
from app.crud import crud_user_profile
from app.schemas import user_profile as user_profile_schema

router = APIRouter()

@router.post("/profile/upload", response_model=user_profile_schema.UserProfile, summary="上传简历文件进行分析")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """
    上传简历文件（PDF 或 DOCX），提取文本内容，
    使用 LLM 进行分析，并将原始文本和分析结果存入数据库。
    """
    content = ""
    try:
        file_bytes = await file.read()
        if file.content_type == "application/pdf":
            with io.BytesIO(file_bytes) as pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                for page in reader.pages:
                    content += page.extract_text() or ""
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            with io.BytesIO(file_bytes) as doc_file:
                doc = docx.Document(doc_file)
                for para in doc.paragraphs:
                    content += para.text + "\n"
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型。请上传 PDF 或 DOCX 文件。")

        if not content.strip():
            raise HTTPException(status_code=400, detail="无法从文件中提取任何文本内容。")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件读取或解析失败: {e}")

    try:
        # 调用 LLM 分析
        structured_data = await llm_client.analyze(content)

        # 创建数据库条目
        profile_in = user_profile_schema.UserProfileCreate(
            raw_content=content,
            structured_profile=structured_data
        )
        created_profile = crud_user_profile.create_user_profile(db, obj_in=profile_in)
        return created_profile

    except Exception as e:
        # 这里的异常可能来自 LLM API 调用或数据库操作
        raise HTTPException(status_code=500, detail=f"处理文件或调用LLM时出错: {e}")
